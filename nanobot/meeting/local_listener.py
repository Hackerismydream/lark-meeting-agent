"""Local transcript live-session runner."""

from __future__ import annotations

import time
from pathlib import Path

from pydantic import Field

from nanobot.meeting.input_provider import (
    LocalTranscriptProvider,
    MeetingInputEventBatch,
    MeetingInputProviderConfig,
    MeetingInputSession,
    ProviderStatus,
)
from nanobot.meeting.live import LiveMeetingWorkflow
from nanobot.meeting.schemas import LiveMeetingState, LiveQAAnswer, MeetingBaseModel, ProcessMeetingResult
from nanobot.meeting.workflow import PostMeetingWorkflow


class LocalTranscriptLiveSession(MeetingBaseModel):
    provider_session: MeetingInputSession
    live_state: LiveMeetingState


class LocalTranscriptLivePollResult(MeetingBaseModel):
    session: LocalTranscriptLiveSession
    batch: MeetingInputEventBatch
    live_state: LiveMeetingState
    ingested_event_count: int


class LocalTranscriptLiveRunReport(MeetingBaseModel):
    session: LocalTranscriptLiveSession
    poll_count: int
    ingested_event_count: int
    qa_answer: LiveQAAnswer | None = None
    postmeeting_result: ProcessMeetingResult | None = None
    status: ProviderStatus
    warnings: list[str] = Field(default_factory=list)


class LocalTranscriptLiveRunner:
    def __init__(self, workspace: Path | str = ".") -> None:
        self.workspace = Path(workspace)
        self.provider = LocalTranscriptProvider(self.workspace)
        self.live = LiveMeetingWorkflow(self.workspace)

    def start(
        self,
        *,
        transcript_file: Path | str,
        meeting_id: str,
        title: str = "local transcript meeting",
    ) -> LocalTranscriptLiveSession:
        live_state = self.live.start(meeting_id, title)
        provider_session = self.provider.start(
            MeetingInputProviderConfig(
                provider_name=self.provider.provider_name,
                meeting_id=meeting_id,
                title=title,
                source_path=str(transcript_file),
                live_run_id=live_state.live_run_id,
                append_mode=True,
            )
        )
        return LocalTranscriptLiveSession(provider_session=provider_session, live_state=live_state)

    def poll(self, session: LocalTranscriptLiveSession) -> LocalTranscriptLivePollResult:
        batch = self.provider.poll(session.provider_session)
        state = session.live_state
        ingested = 0
        for event in batch.events:
            state = self.live.ingest(event)
            ingested += 1
        if not batch.events:
            state = self.live.memory.load_live_state(session.live_state.live_run_id)
        updated = LocalTranscriptLiveSession(provider_session=batch.session, live_state=state)
        return LocalTranscriptLivePollResult(
            session=updated,
            batch=batch,
            live_state=state,
            ingested_event_count=ingested,
        )

    def qa(self, session: LocalTranscriptLiveSession, question: str) -> LiveQAAnswer:
        return self.live.qa(session.live_state.live_run_id, question)

    def stop(self, session: LocalTranscriptLiveSession) -> LocalTranscriptLiveSession:
        self.provider.stop(session.provider_session)
        stopped_provider = session.provider_session.model_copy(update={"status": ProviderStatus.STOPPED})
        return LocalTranscriptLiveSession(provider_session=stopped_provider, live_state=session.live_state)

    def finalize(
        self,
        session: LocalTranscriptLiveSession,
        *,
        create_doc: bool = True,
        create_tasks: bool = True,
        send_message: bool = False,
        chat_id: str | None = None,
        analyzer_mode: str = "fake",
    ) -> ProcessMeetingResult:
        state = self.live.memory.load_live_state(session.live_state.live_run_id)
        return PostMeetingWorkflow(self.workspace, provider_mode="fake", analyzer_mode=analyzer_mode).process_transcript_segments(
            state.meeting_id,
            state.title,
            state.transcript_segments,
            create_doc=create_doc,
            create_tasks=create_tasks,
            send_message=send_message,
            chat_id=chat_id,
            dry_run=True,
            provider_mode="fake",
            analyzer_mode=analyzer_mode,
            source="local_transcript_live",
        )

    def run(
        self,
        *,
        transcript_file: Path | str,
        meeting_id: str,
        title: str = "local transcript meeting",
        max_polls: int = 1,
        poll_interval_sec: float = 0.0,
        question: str | None = None,
        finalize: bool = False,
        create_doc: bool = True,
        create_tasks: bool = True,
        send_message: bool = False,
        chat_id: str | None = None,
        analyzer_mode: str = "fake",
    ) -> LocalTranscriptLiveRunReport:
        session = self.start(transcript_file=transcript_file, meeting_id=meeting_id, title=title)
        total_ingested = 0
        poll_count = 0
        try:
            for index in range(max(1, max_polls)):
                poll = self.poll(session)
                session = poll.session
                total_ingested += poll.ingested_event_count
                poll_count += 1
                if poll_interval_sec > 0 and index < max_polls - 1:
                    time.sleep(poll_interval_sec)
            qa_answer = self.qa(session, question) if question else None
            postmeeting = None
            if finalize:
                postmeeting = self.finalize(
                    session,
                    create_doc=create_doc,
                    create_tasks=create_tasks,
                    send_message=send_message,
                    chat_id=chat_id,
                    analyzer_mode=analyzer_mode,
                )
            return LocalTranscriptLiveRunReport(
                session=session,
                poll_count=poll_count,
                ingested_event_count=total_ingested,
                qa_answer=qa_answer,
                postmeeting_result=postmeeting,
                status=session.provider_session.status,
            )
        finally:
            self.stop(session)
