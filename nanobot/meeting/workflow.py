"""Deterministic post-meeting workflow."""

from __future__ import annotations

import uuid
from pathlib import Path

from nanobot.meeting.analyzer import create_analyzer
from nanobot.meeting.errors import MeetingNotFoundError, TranscriptNotFoundError
from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.normalizer import TranscriptNormalizer
from nanobot.meeting.schemas import (
    ApprovalStatus,
    ExecutionStatus,
    Meeting,
    MeetingRefType,
    ProcessMeetingInput,
    ProcessMeetingResult,
    ProviderMode,
    Run,
    RunStatus,
)
from nanobot.meeting.write_plan import WritePlanBuilder


class PostMeetingWorkflow:
    def __init__(
        self,
        workspace: Path | str,
        provider_mode: str = "fake",
        analyzer_mode: str = "fake",
    ) -> None:
        self.workspace = Path(workspace)
        self.provider_mode = provider_mode
        self.analyzer_mode = analyzer_mode
        self.normalizer = TranscriptNormalizer()
        self.memory = MeetingMemoryStore(self.workspace)

    def process(self, request: ProcessMeetingInput) -> ProcessMeetingResult:
        if request.meeting_ref.type == MeetingRefType.TRANSCRIPT_FILE:
            if not request.meeting_ref.value:
                raise TranscriptNotFoundError("transcript_file requires a path")
            return self.process_transcript_file(
                Path(request.meeting_ref.value),
                create_doc=request.create_doc,
                create_tasks=request.create_tasks,
                send_message=request.send_message,
                chat_id=request.chat_id,
                dry_run=request.dry_run,
            )
        if request.meeting_ref.type == MeetingRefType.LATEST_ENDED:
            return self.process_latest_ended(request)
        raise MeetingNotFoundError(f"unsupported meeting ref: {request.meeting_ref.type}")

    def process_transcript_file(
        self,
        transcript_file: Path | str,
        *,
        create_doc: bool = True,
        create_tasks: bool = True,
        send_message: bool = False,
        chat_id: str | None = None,
        dry_run: bool = True,
    ) -> ProcessMeetingResult:
        path = Path(transcript_file)
        if not path.exists():
            raise TranscriptNotFoundError(str(path))
        meeting = Meeting(meeting_id=f"fixture-{path.stem}", title=path.stem, source="transcript_file")
        return self._run(meeting, path.read_text(), create_doc, create_tasks, send_message, chat_id, dry_run)

    def process_latest_ended(self, request: ProcessMeetingInput) -> ProcessMeetingResult:
        adapter = self._adapter(request.provider_mode)
        search = adapter.execute("vc.search", {"query": request.meeting_ref.query}, dry_run=False)
        meetings = _list_items(search)
        if not meetings:
            minutes_search = adapter.execute("minutes.search", {"query": request.meeting_ref.query}, dry_run=False)
            minute_items = _list_items(minutes_search)
            for minute in minute_items:
                transcript = _extract_text(minute)
                token = minute.get("minute_token") or minute.get("token") or minute.get("id")
                if not transcript and token:
                    note_result = adapter.execute("vc.notes", {"minute_token": token}, dry_run=False)
                    transcript = _extract_text(note_result)
                if transcript:
                    meeting = Meeting(
                        meeting_id=str(token or "minute"),
                        title=str(minute.get("title") or minute.get("topic") or "妙记"),
                        source="lark-cli",
                        external_ids={"minute_token": str(token or "")},
                    )
                    return self._run(
                        meeting,
                        transcript,
                        request.create_doc,
                        request.create_tasks,
                        request.send_message,
                        request.chat_id,
                        request.dry_run,
                    )
            raise MeetingNotFoundError("no ended meeting found")
        last_error: str | None = None
        for raw in meetings:
            meeting_id = str(raw.get("meeting_id") or raw.get("id") or "")
            if not meeting_id:
                continue
            notes = adapter.execute("vc.notes", {"meeting_id": meeting_id}, dry_run=False)
            transcript = _extract_text(notes)
            if not transcript and (token := _first_value(notes, raw, "minute_token", "token")):
                fetched = adapter.execute("docs.fetch", {"doc": token}, dry_run=False)
                transcript = _extract_text(fetched)
            if not transcript:
                last_error = _first_note_error(notes) or "meeting has no transcript content"
                continue
            meeting = Meeting(
                meeting_id=meeting_id,
                title=str(raw.get("title") or raw.get("topic") or raw.get("display_info") or "会议"),
                start_time=raw.get("start_time"),
                end_time=raw.get("end_time"),
                source="lark-cli",
                external_ids={"minute_token": str(_first_value(notes, raw, "minute_token", "token") or "")},
            )
            return self._run(
                meeting,
                str(transcript),
                request.create_doc,
                request.create_tasks,
                request.send_message,
                request.chat_id,
                request.dry_run,
            )
        raise TranscriptNotFoundError(last_error or "meeting has no transcript content")

    def approve(self, run_id: str, operation_ids: list[str]):
        run = self.memory.load_run_snapshot(run_id)
        if not run.write_plan:
            raise TranscriptNotFoundError("run has no write plan")
        adapter = self._adapter(self.provider_mode)
        selected = set(operation_ids)
        for operation in run.write_plan.operations:
            if operation.operation_id not in selected:
                operation.execution_status = ExecutionStatus.SKIPPED
                operation.approval_status = ApprovalStatus.REJECTED
                continue
            if operation.approval_status == ApprovalStatus.MISSING_TARGET:
                operation.execution_status = ExecutionStatus.SKIPPED
                operation.error = "missing target"
                continue
            operation.approval_status = ApprovalStatus.APPROVED
            try:
                result = adapter.execute(
                    operation.operation_type.value,
                    operation.dry_run_payload,
                    dry_run=False,
                    approval_status=ApprovalStatus.APPROVED,
                )
                operation.result = result
                operation.execution_status = ExecutionStatus.COMPLETED
            except Exception as exc:
                operation.error = str(exc)
                operation.execution_status = ExecutionStatus.FAILED
        run.status = RunStatus.COMPLETED
        self.memory.save_run_snapshot(run)
        self.memory.persist_audit(adapter.audit_events)
        return ProcessMeetingResult(
            run_id=run.run_id,
            status=run.status,
            meeting=run.meeting,
            minutes=run.minutes,
            write_plan=run.write_plan,
        )

    def _run(
        self,
        meeting: Meeting,
        transcript: str,
        create_doc: bool,
        create_tasks: bool,
        send_message: bool,
        chat_id: str | None,
        dry_run: bool,
    ) -> ProcessMeetingResult:
        run_id = str(uuid.uuid4())
        segments = self.normalizer.normalize_text(meeting.meeting_id, transcript)
        minutes = create_analyzer(self.analyzer_mode).analyze(meeting.meeting_id, meeting.title, segments)
        write_plan = WritePlanBuilder().build(
            run_id=run_id,
            meeting=meeting,
            minutes=minutes,
            create_doc=create_doc,
            create_tasks=create_tasks,
            send_message=send_message,
            chat_id=chat_id,
        )
        status = RunStatus.APPROVAL_REQUIRED if write_plan.operations else RunStatus.COMPLETED
        run = Run(
            run_id=run_id,
            status=status,
            meeting=meeting,
            transcript_segments=segments,
            minutes=minutes,
            write_plan=write_plan,
        )
        paths = self.memory.persist_run(run)
        paths.append(str(self.memory.save_run_snapshot(run)))
        return ProcessMeetingResult(
            run_id=run_id,
            status=status,
            meeting=meeting,
            minutes=minutes,
            write_plan=write_plan,
            persisted_paths=paths,
        )

    def _adapter(self, mode: str | ProviderMode) -> LarkToolAdapter:
        value = ProviderMode(mode).value
        if value == "fake":
            return LarkToolAdapter.fake(self.workspace)
        return LarkToolAdapter.cli(self.workspace)


def _list_items(payload: dict) -> list[dict]:
    for value in (payload.get("meetings"), payload.get("items")):
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("items", "meetings", "minutes", "notes"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _extract_text(payload: dict) -> str | None:
    for key in ("transcript", "content", "text", "markdown"):
        value = payload.get(key)
        if value:
            return str(value)
    for item in _list_items(payload):
        for key in ("transcript", "content", "text", "markdown"):
            value = item.get(key)
            if value:
                return str(value)
    return None


def _first_value(primary: dict, secondary: dict, *keys: str):
    for source in (primary, secondary):
        for key in keys:
            value = source.get(key)
            if value:
                return value
        for item in _list_items(source):
            for key in keys:
                value = item.get(key)
                if value:
                    return value
    return None


def _first_note_error(payload: dict) -> str | None:
    for item in _list_items(payload):
        if error := item.get("error"):
            return str(error)
    if error := payload.get("error"):
        return str(error)
    return None


def process_input(workspace: Path | str, request: ProcessMeetingInput) -> ProcessMeetingResult:
    workflow = PostMeetingWorkflow(workspace, request.provider_mode.value, request.analyzer_mode.value)
    return workflow.process(request)
