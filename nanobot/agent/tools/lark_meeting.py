"""nanobot tool wrapper for deterministic meeting workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.schemas import MeetingRef, MeetingRefType, ProcessMeetingInput
from nanobot.meeting.workflow import PostMeetingWorkflow


class LarkMeetingTool(Tool):
    def __init__(self, workspace: Path | str | None = None) -> None:
        self.workspace = Path(workspace or ".")

    @property
    def name(self) -> str:
        return "lark_meeting"

    @property
    def description(self) -> str:
        return "Process Lark meeting transcripts, approve write plans, and answer source-grounded meeting QA."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["process", "approve", "qa", "status"]},
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
                "provider_mode": {"type": "string", "enum": ["fake", "cli"]},
                "analyzer_mode": {"type": "string", "enum": ["fake", "llm"]},
                "dry_run": {"type": "boolean"},
            },
            "required": ["action"],
        }

    async def execute(self, **kwargs: Any) -> str:
        action = kwargs.get("action")
        provider_mode = kwargs.get("provider_mode") or "fake"
        analyzer_mode = kwargs.get("analyzer_mode") or "fake"
        workflow = PostMeetingWorkflow(self.workspace, provider_mode, analyzer_mode)
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
        return f"Error: unknown action {action}"
