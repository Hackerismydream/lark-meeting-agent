"""Production Feishu bot command routing and policy primitives."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

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
    RunStatus,
)
from nanobot.meeting.workflow import PostMeetingWorkflow

CommandAction = Literal["process", "approve", "reject", "status", "qa", "prebrief", "ignored", "unknown"]


class MeetingBotContext(BaseModel):
    sender_id: str
    chat_id: str | None = None
    chat_type: Literal["dm", "group"] = "dm"
    mentioned: bool = False


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

    def should_ignore_group_message(self, context: MeetingBotContext, text: str) -> bool:
        if context.chat_type != "group" or not self.group_requires_mention_or_command:
            return False
        return not context.mentioned and not text.strip().startswith("/meeting")


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
        if self.policy.should_ignore_group_message(context, text):
            return MeetingBotReply(status="ignored", text="")
        if not self.policy.is_allowed(context):
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
            run = MeetingMemoryStore(self.workspace).load_run_snapshot(command.run_id)
            self.repository.save_run(run)
            return MeetingBotReply(status="ok", text=run.model_dump_json(indent=2), run_id=run.run_id)
        if command.action == "approve":
            if not self.policy.can_approve(context):
                return MeetingBotReply(status="denied", text="无权限审批写操作。")
            result = PostMeetingWorkflow(self.workspace, self.provider_mode, self.analyzer_mode).approve(
                command.run_id or "",
                command.operation_ids,
            )
            run = MeetingMemoryStore(self.workspace).load_run_snapshot(result.run_id)
            self.repository.save_run(run)
            completed = [
                op.operation_id
                for op in result.write_plan.operations
                if op.execution_status == ExecutionStatus.COMPLETED
            ] if result.write_plan else []
            return MeetingBotReply(status="ok", text=f"已执行已审批操作: {', '.join(completed) or '无'}", run_id=result.run_id)
        if command.action == "reject":
            if not self.policy.can_approve(context):
                return MeetingBotReply(status="denied", text="无权限拒绝写操作。")
            result = PostMeetingWorkflow(self.workspace, self.provider_mode, self.analyzer_mode).reject(command.run_id or "")
            run = MeetingMemoryStore(self.workspace).load_run_snapshot(result.run_id)
            self.repository.save_run(run)
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
