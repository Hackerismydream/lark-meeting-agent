"""nanobot tool wrapper for deterministic meeting workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.meeting.evals import LifecycleEvaluator
from nanobot.meeting.live import LiveMeetingWorkflow
from nanobot.meeting.live_lark import LiveLarkMeetingWorkflow
from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.production import MeetingAgentAccessPolicy, MeetingBotContext, ProductionMeetingBot
from nanobot.meeting.schemas import (
    ApprovalStatus,
    LiveEventKind,
    LiveMeetingEvent,
    MeetingRef,
    MeetingRefType,
    MeetingType,
    PreBriefInput,
    ProcessMeetingInput,
)
from nanobot.meeting.workflow import PostMeetingWorkflow


class LarkMeetingTool(Tool):
    def __init__(self, workspace: Path | str | None = None) -> None:
        self.workspace = Path(workspace or ".")

    @property
    def name(self) -> str:
        return "lark_meeting"

    @property
    def description(self) -> str:
        return "Prepare, understand, process, approve, evaluate, and answer source-grounded Lark meeting workflows."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "bot_message",
                        "prebrief",
                        "live_join",
                        "live_poll",
                        "live_leave",
                        "live_ingest",
                        "live_qa",
                        "process",
                        "approve",
                        "qa",
                        "status",
                        "evaluate",
                    ],
                },
                "message_text": {"type": ["string", "null"]},
                "sender_id": {"type": ["string", "null"]},
                "sender_open_id": {"type": ["string", "null"]},
                "bot_chat_type": {"type": "string", "enum": ["dm", "group"]},
                "mentioned": {"type": "boolean"},
                "allowed_users": {"type": "array", "items": {"type": "string"}},
                "allowed_chat_ids": {"type": "array", "items": {"type": "string"}},
                "admin_users": {"type": "array", "items": {"type": "string"}},
                "write_approvers": {"type": "array", "items": {"type": "string"}},
                "live_approvers": {"type": "array", "items": {"type": "string"}},
                "meeting_ref_type": {
                    "type": "string",
                    "enum": ["latest_ended", "meeting_id", "minute_token", "transcript_file"],
                },
                "meeting_ref_value": {"type": ["string", "null"]},
                "query": {"type": ["string", "null"]},
                "run_id": {"type": ["string", "null"]},
                "operation_ids": {"type": "array", "items": {"type": "string"}},
                "question": {"type": ["string", "null"]},
                "create_doc": {"type": "boolean"},
                "create_tasks": {"type": "boolean"},
                "send_message": {"type": "boolean"},
                "chat_id": {"type": ["string", "null"]},
                "provider_mode": {"type": "string", "enum": ["fake", "cli", "oapi"]},
                "analyzer_mode": {"type": "string", "enum": ["fake", "llm"]},
                "dry_run": {"type": "boolean"},
                "meeting_type": {
                    "type": "string",
                    "enum": [
                        "customer_meeting",
                        "project_sync",
                        "requirement_review",
                        "technical_review",
                        "incident_review",
                        "one_on_one",
                        "general",
                    ],
                },
                "project": {"type": ["string", "null"]},
                "customer": {"type": ["string", "null"]},
                "meeting_number": {"type": ["string", "null"]},
                "meeting_password": {"type": ["string", "null"]},
                "approve_visible_join": {"type": "boolean"},
                "approve_visible_leave": {"type": "boolean"},
                "page_token": {"type": ["string", "null"]},
                "live_run_id": {"type": ["string", "null"]},
                "event_text": {"type": ["string", "null"]},
                "event_kind": {
                    "type": "string",
                    "enum": ["transcript_delta", "topic_change", "participant_join", "participant_leave", "marker"],
                },
                "speaker": {"type": ["string", "null"]},
                "timestamp": {"type": ["string", "null"]},
                "cases_file": {"type": ["string", "null"]},
                "output_file": {"type": ["string", "null"]},
            },
            "required": ["action"],
        }

    def _policy_from_kwargs(self, kwargs: dict[str, Any]) -> MeetingAgentAccessPolicy:
        return MeetingAgentAccessPolicy(
            allowed_users=set(kwargs.get("allowed_users") or []),
            allowed_chat_ids=set(kwargs.get("allowed_chat_ids") or []),
            admin_users=set(kwargs.get("admin_users") or []),
            write_approvers=set(kwargs.get("write_approvers") or []),
            live_approvers=set(kwargs.get("live_approvers") or []),
        )

    def _context_from_kwargs(self, kwargs: dict[str, Any]) -> MeetingBotContext | None:
        sender_id = kwargs.get("sender_id") or kwargs.get("sender_open_id")
        if not sender_id:
            return None
        return MeetingBotContext(
            sender_id=str(sender_id),
            chat_id=kwargs.get("chat_id"),
            chat_type=kwargs.get("bot_chat_type") or "dm",
            mentioned=bool(kwargs.get("mentioned", False)),
        )

    def _require_write_approver(self, kwargs: dict[str, Any]) -> str | None:
        context = self._context_from_kwargs(kwargs)
        if context is None:
            return "Error: production context is required for approve"
        if not self._policy_from_kwargs(kwargs).can_approve(context):
            return "Error: sender is not allowed to approve write operations"
        return None

    def _require_live_approver(self, kwargs: dict[str, Any]) -> str | None:
        context = self._context_from_kwargs(kwargs)
        if context is None:
            return "Error: production context is required for live meeting control"
        if not self._policy_from_kwargs(kwargs).can_control_live(context):
            return "Error: sender is not allowed to approve live meeting control"
        return None

    async def execute(self, **kwargs: Any) -> str:
        action = kwargs.get("action")
        provider_mode = kwargs.get("provider_mode") or "fake"
        analyzer_mode = kwargs.get("analyzer_mode") or "fake"
        workflow = PostMeetingWorkflow(self.workspace, provider_mode, analyzer_mode)
        if action == "bot_message":
            message_text = kwargs.get("message_text") or kwargs.get("query")
            sender_id = kwargs.get("sender_id") or kwargs.get("sender_open_id")
            if not message_text:
                return "Error: message_text is required for bot_message"
            if not sender_id:
                return "Error: sender_id is required for bot_message"
            policy = self._policy_from_kwargs(kwargs)
            reply = ProductionMeetingBot(
                workspace=self.workspace,
                policy=policy,
                provider_mode=provider_mode,
                analyzer_mode=analyzer_mode,
            ).handle_message(
                MeetingBotContext(
                    sender_id=str(sender_id),
                    chat_id=kwargs.get("chat_id"),
                    chat_type=kwargs.get("bot_chat_type") or "dm",
                    mentioned=bool(kwargs.get("mentioned", False)),
                ),
                str(message_text),
            )
            return reply.model_dump_json(indent=2)
        if action == "prebrief":
            ref = MeetingRef(
                type=MeetingRefType(kwargs.get("meeting_ref_type") or "latest_ended"),
                value=kwargs.get("meeting_ref_value"),
                query=kwargs.get("query"),
            )
            result = PreBriefWorkflow(self.workspace, provider_mode).generate(
                PreBriefInput(
                    meeting_ref=ref,
                    provider_mode=provider_mode,
                    meeting_type=MeetingType(kwargs.get("meeting_type") or "general"),
                    project=kwargs.get("project"),
                    customer=kwargs.get("customer"),
                )
            )
            return result.model_dump_json(indent=2)
        if action == "live_join":
            policy_error = self._require_live_approver(kwargs)
            if policy_error:
                return policy_error
            meeting_number = kwargs.get("meeting_number")
            if not meeting_number:
                return "Error: meeting_number is required for live_join"
            approved = ApprovalStatus.APPROVED if kwargs.get("approve_visible_join") else ApprovalStatus.PENDING
            result = LiveLarkMeetingWorkflow(self.workspace, provider_mode).join(
                meeting_number=str(meeting_number),
                password=kwargs.get("meeting_password"),
                dry_run=not bool(kwargs.get("approve_visible_join")),
                approval_status=approved,
            )
            return result.model_dump_json(indent=2)
        if action == "live_poll":
            meeting_id = kwargs.get("meeting_ref_value") or kwargs.get("meeting_id")
            live_run_id = kwargs.get("live_run_id")
            if not meeting_id:
                return "Error: meeting_ref_value is required for live_poll"
            if not live_run_id:
                return "Error: live_run_id is required for live_poll"
            result = LiveLarkMeetingWorkflow(self.workspace, provider_mode).poll(
                str(meeting_id),
                live_run_id=str(live_run_id),
                page_token=kwargs.get("page_token"),
            )
            return result.model_dump_json(indent=2)
        if action == "live_leave":
            policy_error = self._require_live_approver(kwargs)
            if policy_error:
                return policy_error
            meeting_id = kwargs.get("meeting_ref_value") or kwargs.get("meeting_id")
            if not meeting_id:
                return "Error: meeting_ref_value is required for live_leave"
            approved = ApprovalStatus.APPROVED if kwargs.get("approve_visible_leave") else ApprovalStatus.PENDING
            result = LiveLarkMeetingWorkflow(self.workspace, provider_mode).leave(
                str(meeting_id),
                dry_run=not bool(kwargs.get("approve_visible_leave")),
                approval_status=approved,
            )
            return json.dumps(result, ensure_ascii=False, indent=2)
        if action == "live_ingest":
            live_run_id = kwargs.get("live_run_id")
            meeting_id = kwargs.get("meeting_ref_value") or kwargs.get("meeting_id") or "live-meeting"
            if not live_run_id:
                state = LiveMeetingWorkflow(self.workspace).start(str(meeting_id), str(kwargs.get("query") or "live meeting"))
                live_run_id = state.live_run_id
            event = LiveMeetingEvent(
                event_id=str(kwargs.get("event_id") or "tool-event"),
                live_run_id=str(live_run_id),
                meeting_id=str(meeting_id),
                kind=LiveEventKind(kwargs.get("event_kind") or "transcript_delta"),
                text=kwargs.get("event_text") or kwargs.get("query"),
                speaker_name=kwargs.get("speaker"),
                timestamp=kwargs.get("timestamp"),
            )
            return LiveMeetingWorkflow(self.workspace).ingest(event).model_dump_json(indent=2)
        if action == "live_qa":
            live_run_id = kwargs.get("live_run_id")
            question = kwargs.get("question")
            if not live_run_id:
                return "Error: live_run_id is required for live_qa"
            if not question:
                return "Error: question is required for live_qa"
            return LiveMeetingWorkflow(self.workspace).qa(str(live_run_id), str(question)).model_dump_json(indent=2)
        if action == "process":
            ref = MeetingRef(
                type=MeetingRefType(kwargs.get("meeting_ref_type") or "latest_ended"),
                value=kwargs.get("meeting_ref_value"),
                query=kwargs.get("query"),
            )
            result = workflow.process(
                ProcessMeetingInput(
                    meeting_ref=ref,
                    provider_mode=provider_mode,
                    analyzer_mode=analyzer_mode,
                    create_doc=bool(kwargs.get("create_doc", True)),
                    create_tasks=bool(kwargs.get("create_tasks", True)),
                    send_message=bool(kwargs.get("send_message", False)),
                    chat_id=kwargs.get("chat_id"),
                    dry_run=bool(kwargs.get("dry_run", True)),
                )
            )
            return result.model_dump_json(indent=2)
        if action == "approve":
            policy_error = self._require_write_approver(kwargs)
            if policy_error:
                return policy_error
            run_id = kwargs.get("run_id")
            if not run_id:
                return "Error: run_id is required for approve"
            result = workflow.approve(str(run_id), list(kwargs.get("operation_ids") or []))
            return result.model_dump_json(indent=2)
        if action == "qa":
            question = kwargs.get("question")
            if not question:
                return "Error: question is required for qa"
            return MeetingMemoryStore(self.workspace).qa(str(question)).model_dump_json(indent=2)
        if action == "status":
            run_id = kwargs.get("run_id")
            if not run_id:
                return "Error: run_id is required for status"
            run = MeetingMemoryStore(self.workspace).load_run_snapshot(str(run_id))
            return run.model_dump_json(indent=2)
        if action == "evaluate":
            cases_file = kwargs.get("cases_file") or "tests/fixtures/meeting/evaluation/lifecycle_cases.json"
            report = LifecycleEvaluator(self.workspace).evaluate_file(cases_file, kwargs.get("output_file"))
            return report.model_dump_json(indent=2)
        return f"Error: unknown action {action}"
