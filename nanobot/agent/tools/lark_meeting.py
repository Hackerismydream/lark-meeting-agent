"""nanobot tool wrapper for deterministic meeting workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.meeting.evals import LifecycleEvaluator
from nanobot.meeting.live import LiveMeetingWorkflow
from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.schemas import (
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
                    "enum": ["prebrief", "live_ingest", "live_qa", "process", "approve", "qa", "status", "evaluate"],
                },
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

    async def execute(self, **kwargs: Any) -> str:
        action = kwargs.get("action")
        provider_mode = kwargs.get("provider_mode") or "fake"
        analyzer_mode = kwargs.get("analyzer_mode") or "fake"
        workflow = PostMeetingWorkflow(self.workspace, provider_mode, analyzer_mode)
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
