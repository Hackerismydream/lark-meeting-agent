"""Production Feishu bot command routing and policy primitives."""

from __future__ import annotations

import json
import re
from contextlib import nullcontext
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.repository import JsonlMeetingRepository, MeetingRepository
from nanobot.meeting.schemas import (
    ExecutionStatus,
    MeetingRef,
    MeetingRefType,
    MeetingType,
    PreBriefInput,
    ProcessMeetingInput,
    ApprovalStatus,
    ExecutionStatus,
    ProviderMode,
    ReadOrWrite,
    RunStatus,
    ToolCallAuditEvent,
)
from nanobot.meeting.workflow import PostMeetingWorkflow

CommandAction = Literal["process", "approve", "reject", "status", "qa", "prebrief", "ignored", "unknown"]


class MeetingBotContext(BaseModel):
    sender_id: str
    chat_id: str | None = None
    chat_type: Literal["dm", "group"] = "dm"
    mentioned: bool = False
    text: str | None = None
    message_id: str | None = None


class FeishuMeetingMessage(BaseModel):
    context: MeetingBotContext
    text: str


class MeetingBotReply(BaseModel):
    status: str
    text: str
    run_id: str | None = None
    data: dict = Field(default_factory=dict)


@dataclass
class MeetingBotCommand:
    action: CommandAction
    run_id: str | None = None
    operation_ids: list[str] = field(default_factory=list)
    question: str | None = None
    query: str | None = None
    dry_run: bool = True


@dataclass
class MeetingAgentAccessPolicy:
    allowed_users: set[str] = field(default_factory=set)
    allowed_chat_ids: set[str] = field(default_factory=set)
    admin_users: set[str] = field(default_factory=set)
    write_approvers: set[str] = field(default_factory=set)
    live_approvers: set[str] = field(default_factory=set)
    group_requires_mention_or_command: bool = True

    def is_allowed(self, context: MeetingBotContext) -> bool:
        if context.sender_id in self.admin_users:
            return True
        if context.sender_id not in self.allowed_users and context.sender_id not in self.write_approvers:
            return False
        if context.chat_type == "group" and self.allowed_chat_ids and context.chat_id not in self.allowed_chat_ids:
            return False
        return True

    def can_approve(self, context: MeetingBotContext) -> bool:
        return context.sender_id in self.admin_users or context.sender_id in self.write_approvers

    def can_control_live(self, context: MeetingBotContext) -> bool:
        return context.sender_id in self.admin_users or context.sender_id in self.live_approvers

    def should_ignore_group_message(self, context: MeetingBotContext, text: str) -> bool:
        if context.chat_type != "group" or not self.group_requires_mention_or_command:
            return False
        return not context.mentioned and not text.strip().startswith("/meeting")


def _dig(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _extract_feishu_text(message: dict[str, Any]) -> str:
    text = message.get("text")
    if isinstance(text, str):
        return text.strip()
    content = message.get("content")
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return content.strip()
    elif isinstance(content, dict):
        parsed = content
    else:
        parsed = {}
    value = parsed.get("text") or parsed.get("content") or ""
    return str(value).strip()


def _is_bot_mentioned(message: dict[str, Any], bot_open_id: str | None) -> bool:
    if isinstance(message.get("mentioned"), bool):
        return bool(message["mentioned"])
    mentions = message.get("mentions") or []
    if not mentions:
        return False
    if not bot_open_id:
        return True
    for mention in mentions:
        open_id = _dig(mention, "id", "open_id") or mention.get("open_id") or _dig(mention, "id", "user_id")
        if open_id == bot_open_id:
            return True
    return False


def map_feishu_message_event(event: dict[str, Any], bot_open_id: str | None = None) -> FeishuMeetingMessage:
    """Map SDK-like or already-normalized Feishu message payloads to bot input."""

    message = event.get("message") if isinstance(event.get("message"), dict) else event
    sender_id = (
        _dig(event, "sender", "sender_id", "open_id")
        or _dig(event, "sender", "sender_id", "user_id")
        or event.get("sender_id")
        or message.get("sender_id")
    )
    if not sender_id:
        raise ValueError("Feishu message event missing sender_id")
    chat_id = message.get("chat_id") or event.get("chat_id")
    raw_chat_type = str(message.get("chat_type") or event.get("chat_type") or "p2p")
    chat_type: Literal["dm", "group"] = "group" if raw_chat_type == "group" else "dm"
    message_id = message.get("message_id") or event.get("message_id")
    text = _extract_feishu_text(message)
    context = MeetingBotContext(
        sender_id=str(sender_id),
        chat_id=str(chat_id) if chat_id else None,
        chat_type=chat_type,
        mentioned=_is_bot_mentioned(message, bot_open_id),
        text=text,
        message_id=str(message_id) if message_id else None,
    )
    return FeishuMeetingMessage(context=context, text=text)


class ProductionConfigWarning(BaseModel):
    code: str
    message: str


def validate_production_config(config: dict) -> list[ProductionConfigWarning]:
    warnings: list[ProductionConfigWarning] = []
    channels = config.get("channels", {})
    feishu = channels.get("feishu", {}) if isinstance(channels, dict) else {}
    allow_from = feishu.get("allowFrom", [])
    if "*" in allow_from:
        warnings.append(ProductionConfigWarning(code="wildcard_allow_from", message="Feishu allowFrom contains wildcard"))
    tools = config.get("tools", {})
    exec_cfg = tools.get("exec", {}) if isinstance(tools, dict) else {}
    if exec_cfg.get("enable") is not False:
        warnings.append(ProductionConfigWarning(code="exec_enabled", message="Production config should set tools.exec.enable=false"))
    if tools.get("restrictToWorkspace") is not True:
        warnings.append(
            ProductionConfigWarning(code="workspace_unrestricted", message="Production config should set tools.restrictToWorkspace=true")
        )
    meeting = config.get("meetingAgent", {})
    if not meeting.get("writeApprovers"):
        warnings.append(ProductionConfigWarning(code="missing_approvers", message="No write approvers configured"))
    return warnings


def parse_meeting_command(text: str) -> MeetingBotCommand:
    normalized = text.strip()
    if not normalized:
        return MeetingBotCommand(action="ignored")
    if normalized.startswith("整理最近一场会"):
        return MeetingBotCommand(action="process", dry_run=True)
    if normalized.startswith("查看待审批操作"):
        return MeetingBotCommand(action="status")
    if normalized.startswith("帮我准备") or normalized.startswith("准备"):
        return MeetingBotCommand(action="prebrief", query=normalized)
    if normalized.startswith("查询：") or normalized.startswith("查询:"):
        return MeetingBotCommand(action="qa", question=normalized.split(":", 1)[-1].split("：", 1)[-1].strip())
    if not normalized.startswith("/meeting"):
        return MeetingBotCommand(action="unknown")
    parts = normalized.split()
    if len(parts) < 2:
        return MeetingBotCommand(action="unknown")
    command = parts[1]
    if command == "process":
        return MeetingBotCommand(action="process", query=" ".join(parts[2:]) or None, dry_run=True)
    if command == "prebrief":
        return MeetingBotCommand(action="prebrief", query=" ".join(parts[2:]) or None)
    if command == "qa":
        return MeetingBotCommand(action="qa", question=" ".join(parts[2:]).strip() or None)
    if command == "status":
        return MeetingBotCommand(action="status", run_id=parts[2] if len(parts) > 2 else None)
    if command == "approve" and len(parts) >= 4:
        operation_ids = [item for part in parts[3:] for item in re.split(r"[,，]", part) if item]
        return MeetingBotCommand(action="approve", run_id=parts[2], operation_ids=operation_ids)
    if command == "reject" and len(parts) >= 3:
        return MeetingBotCommand(action="reject", run_id=parts[2])
    return MeetingBotCommand(action="unknown")


def render_approval_prompt(result) -> str:
    minutes = result.minutes
    plan = result.write_plan
    lines = ["已生成会议纪要预览，尚未写入飞书。", "未审批前不会执行任何飞书写入。", "", f"Run ID: {result.run_id}", ""]
    if minutes:
        lines.extend(["摘要:", minutes.one_sentence_summary, ""])
        if minutes.decisions:
            lines.append("决策:")
            lines.extend(f"- {item.text}" for item in minutes.decisions)
            lines.append("")
        if minutes.action_items:
            lines.append("待办:")
            lines.extend(f"- {item.task} owner={item.owner or 'unassigned'} due={item.due_date or 'no due date'}" for item in minutes.action_items)
            lines.append("")
    operations = plan.operations if plan else []
    if operations:
        lines.append("将创建:")
        lines.extend(f"{idx}. {op.preview} ({op.operation_id})" for idx, op in enumerate(operations, start=1))
        lines.extend(
            [
                "",
                "回复:",
                f"/meeting approve {result.run_id} " + " ".join(op.operation_id for op in operations),
                "或:",
                f"/meeting reject {result.run_id}",
            ]
        )
    else:
        lines.append("没有待写入操作。")
    return "\n".join(lines)


class ProductionMeetingBot:
    def __init__(
        self,
        workspace: Path | str,
        policy: MeetingAgentAccessPolicy,
        repository: MeetingRepository | None = None,
        provider_mode: str = "fake",
        analyzer_mode: str = "fake",
    ) -> None:
        self.workspace = Path(workspace)
        self.policy = policy
        self.repository = repository or JsonlMeetingRepository(self.workspace)
        self.provider_mode = provider_mode
        self.analyzer_mode = analyzer_mode

    def handle_message(self, context: MeetingBotContext, text: str) -> MeetingBotReply:
        if not text and context.text:
            text = context.text
        if self.policy.should_ignore_group_message(context, text):
            return MeetingBotReply(status="ignored", text="")
        if not self.policy.is_allowed(context):
            self._audit_denied(context, "sender_not_allowed")
            return MeetingBotReply(status="denied", text="无权限使用会议 Agent。")
        command = parse_meeting_command(text)
        if command.action == "ignored":
            return MeetingBotReply(status="ignored", text="")
        if command.action == "unknown":
            return MeetingBotReply(status="error", text="无法识别会议命令。请使用 /meeting process|approve|reject|status|qa|prebrief。")
        if command.action == "process":
            result = PostMeetingWorkflow(self.workspace, self.provider_mode, self.analyzer_mode).process(
                ProcessMeetingInput(
                    meeting_ref=MeetingRef(type=MeetingRefType.LATEST_ENDED, query=command.query),
                    provider_mode=self.provider_mode,
                    analyzer_mode=self.analyzer_mode,
                    create_doc=True,
                    create_tasks=True,
                    send_message=False,
                    dry_run=True,
                )
            )
            run = MeetingMemoryStore(self.workspace).load_run_snapshot(result.run_id)
            self.repository.save_run(run)
            return MeetingBotReply(status=str(result.status.value), text=render_approval_prompt(result), run_id=result.run_id)
        if command.action == "qa":
            if not command.question:
                return MeetingBotReply(status="error", text="请提供查询问题。")
            answer = MeetingMemoryStore(self.workspace).qa(command.question)
            return MeetingBotReply(status="ok", text=answer.answer, data=answer.model_dump(mode="json"))
        if command.action == "status":
            if not command.run_id:
                return MeetingBotReply(status="error", text="请提供 run_id。")
            run = self.repository.load_run(command.run_id)
            return MeetingBotReply(status="ok", text=run.model_dump_json(indent=2), run_id=run.run_id)
        if command.action == "approve":
            if not command.run_id or not command.operation_ids:
                return MeetingBotReply(status="error", text="请提供 run_id 和 operation_ids。")
            if not self.policy.can_approve(context):
                self._audit_denied(context, "write_approval_denied")
                return MeetingBotReply(status="denied", text="无权限审批写操作。")
            guard = getattr(self.repository, "approval_guard", None)
            with (guard(command.run_id) if guard else nullcontext()):
                run = self.repository.load_run(command.run_id)
                result = PostMeetingWorkflow(self.workspace, self.provider_mode, self.analyzer_mode).approve_run(
                    run,
                    command.operation_ids,
                )
                updated_run = MeetingMemoryStore(self.workspace).load_run_snapshot(result.run_id)
                self.repository.save_run(updated_run)
            completed = [
                op.operation_id
                for op in result.write_plan.operations
                if op.execution_status == ExecutionStatus.COMPLETED
            ] if result.write_plan else []
            return MeetingBotReply(status="ok", text=f"已执行已审批操作: {', '.join(completed) or '无'}", run_id=result.run_id)
        if command.action == "reject":
            if not command.run_id:
                return MeetingBotReply(status="error", text="请提供 run_id。")
            if not self.policy.can_approve(context):
                self._audit_denied(context, "write_reject_denied")
                return MeetingBotReply(status="denied", text="无权限拒绝写操作。")
            guard = getattr(self.repository, "approval_guard", None)
            with (guard(command.run_id) if guard else nullcontext()):
                run = self.repository.load_run(command.run_id)
                result = PostMeetingWorkflow(self.workspace, self.provider_mode, self.analyzer_mode).reject_run(run)
                updated_run = MeetingMemoryStore(self.workspace).load_run_snapshot(result.run_id)
                self.repository.save_run(updated_run)
            return MeetingBotReply(status=RunStatus.REJECTED.value, text=f"已拒绝 run {result.run_id} 的待写入操作。", run_id=result.run_id)
        if command.action == "prebrief":
            brief = PreBriefWorkflow(self.workspace, self.provider_mode).generate(
                PreBriefInput(
                    meeting_ref=MeetingRef(type=MeetingRefType.LATEST_ENDED, query=command.query),
                    provider_mode=self.provider_mode,
                    meeting_type=MeetingType.GENERAL,
                )
            )
            return MeetingBotReply(status="ok", text=brief.model_dump_json(indent=2), run_id=brief.run_id)
        return MeetingBotReply(status="error", text="unsupported command")

    def handle_feishu_event(self, event: dict[str, Any], bot_open_id: str | None = None) -> MeetingBotReply:
        envelope = map_feishu_message_event(event, bot_open_id=bot_open_id)
        return self.handle_message(envelope.context, envelope.text)

    def _audit_denied(self, context: MeetingBotContext, reason: str) -> None:
        self.repository.save_audit_events(
            [
                ToolCallAuditEvent(
                    audit_id=str(uuid4()),
                    operation_name="production.policy.denied",
                    provider_mode=ProviderMode.FAKE,
                    sanitized_input={
                        "sender_id": context.sender_id,
                        "chat_id": context.chat_id,
                        "chat_type": context.chat_type,
                        "message_id": context.message_id,
                        "reason": reason,
                    },
                    read_or_write=ReadOrWrite.READ,
                    dry_run=True,
                    approval_status=ApprovalStatus.REJECTED,
                    execution_status=ExecutionStatus.FAILED,
                    error_message=reason,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
            ]
        )
