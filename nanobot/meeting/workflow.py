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
        meetings = search.get("meetings") or search.get("items") or []
        if not meetings:
            raise MeetingNotFoundError("no ended meeting found")
        raw = meetings[0]
        meeting_id = str(raw.get("meeting_id") or raw.get("id") or "")
        if not meeting_id:
            raise MeetingNotFoundError("meeting search result has no meeting_id")
        notes = adapter.execute("vc.notes", {"meeting_id": meeting_id}, dry_run=False)
        transcript = notes.get("transcript") or notes.get("content") or notes.get("text")
        if not transcript and (token := notes.get("minute_token") or raw.get("minute_token")):
            fetched = adapter.execute("docs.fetch", {"doc": token}, dry_run=False)
            transcript = fetched.get("content") or fetched.get("text")
        if not transcript:
            raise TranscriptNotFoundError("meeting has no transcript content")
        meeting = Meeting(
            meeting_id=meeting_id,
            title=str(raw.get("title") or notes.get("title") or "会议"),
            start_time=raw.get("start_time"),
            end_time=raw.get("end_time"),
            source="lark-cli",
            external_ids={"minute_token": str(raw.get("minute_token") or "")},
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


def process_input(workspace: Path | str, request: ProcessMeetingInput) -> ProcessMeetingResult:
    workflow = PostMeetingWorkflow(workspace, request.provider_mode.value, request.analyzer_mode.value)
    return workflow.process(request)
