"""Provider-agnostic meeting input sources."""

from __future__ import annotations

import uuid
import wave
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from pydantic import Field, field_validator

from nanobot.meeting.normalizer import TranscriptNormalizer
from nanobot.meeting.schemas import LiveEventKind, LiveMeetingEvent, MeetingBaseModel, TranscriptSegment


class ProviderStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    EXHAUSTED = "exhausted"
    STOPPED = "stopped"
    ERROR = "error"


class MeetingInputProviderConfig(MeetingBaseModel):
    provider_name: str
    meeting_id: str
    title: str = "local meeting"
    source_path: str | None = None
    transcript_path: str | None = None
    live_run_id: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("provider_name", "meeting_id")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be empty")
        return value.strip()


class MeetingInputSession(MeetingBaseModel):
    session_id: str
    provider_name: str
    meeting_id: str
    live_run_id: str
    title: str = "local meeting"
    source_path: str | None = None
    transcript_path: str | None = None
    status: ProviderStatus = ProviderStatus.IDLE
    cursor: int = 0
    metadata: dict[str, str] = Field(default_factory=dict)


class MeetingInputEventBatch(MeetingBaseModel):
    session: MeetingInputSession
    events: list[LiveMeetingEvent] = Field(default_factory=list)
    transcript_segments: list[TranscriptSegment] = Field(default_factory=list)
    status: ProviderStatus
    has_more: bool = False


class MeetingInputProvider(Protocol):
    def start(self, config: MeetingInputProviderConfig) -> MeetingInputSession: ...

    def poll(self, session: MeetingInputSession) -> MeetingInputEventBatch: ...

    def stop(self, session: MeetingInputSession) -> None: ...


class LocalTranscriptProvider:
    provider_name = "local_transcript"

    def __init__(self, workspace: Path | str = ".") -> None:
        self.workspace = Path(workspace)
        self.normalizer = TranscriptNormalizer()

    def start(self, config: MeetingInputProviderConfig) -> MeetingInputSession:
        path = _required_existing_file(config.source_path, self.workspace)
        return MeetingInputSession(
            session_id=str(uuid.uuid4()),
            provider_name=self.provider_name,
            meeting_id=config.meeting_id,
            live_run_id=config.live_run_id or str(uuid.uuid4()),
            title=config.title,
            source_path=str(path),
            status=ProviderStatus.RUNNING,
            metadata=dict(config.metadata),
        )

    def poll(self, session: MeetingInputSession) -> MeetingInputEventBatch:
        if session.status in {ProviderStatus.EXHAUSTED, ProviderStatus.STOPPED}:
            exhausted = session.model_copy(update={"status": ProviderStatus.EXHAUSTED})
            return MeetingInputEventBatch(session=exhausted, status=ProviderStatus.EXHAUSTED)
        if not session.source_path:
            raise ValueError("local transcript session is missing source_path")
        segments = self._load_segments(Path(session.source_path), session.meeting_id)
        pending = segments[session.cursor :]
        events = [_segment_to_event(segment, session.live_run_id) for segment in pending]
        status = ProviderStatus.EXHAUSTED
        updated = session.model_copy(update={"cursor": len(segments), "status": status})
        return MeetingInputEventBatch(
            session=updated,
            events=events,
            transcript_segments=pending,
            status=status,
            has_more=False,
        )

    def stop(self, session: MeetingInputSession) -> None:
        session.status = ProviderStatus.STOPPED

    def _load_segments(self, path: Path, meeting_id: str) -> list[TranscriptSegment]:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            return self.normalizer.normalize_json(meeting_id, text)
        return self.normalizer.normalize_text(meeting_id, text)


class LocalAudioFileProvider:
    provider_name = "local_audio_file"
    supported_suffixes = {".aac", ".flac", ".m4a", ".mp3", ".wav"}

    def __init__(self, workspace: Path | str = ".") -> None:
        self.workspace = Path(workspace)
        self.transcripts = LocalTranscriptProvider(workspace)

    def start(self, config: MeetingInputProviderConfig) -> MeetingInputSession:
        audio_path = _required_existing_file(config.source_path, self.workspace)
        suffix = audio_path.suffix.lower()
        if suffix not in self.supported_suffixes:
            raise ValueError(f"unsupported audio file type: {suffix or '<none>'}")
        transcript_path = _optional_existing_file(config.transcript_path, self.workspace)
        metadata = dict(config.metadata)
        metadata.update(_audio_metadata(audio_path))
        return MeetingInputSession(
            session_id=str(uuid.uuid4()),
            provider_name=self.provider_name,
            meeting_id=config.meeting_id,
            live_run_id=config.live_run_id or str(uuid.uuid4()),
            title=config.title,
            source_path=str(audio_path),
            transcript_path=str(transcript_path) if transcript_path else None,
            status=ProviderStatus.RUNNING,
            metadata=metadata,
        )

    def poll(self, session: MeetingInputSession) -> MeetingInputEventBatch:
        if session.status in {ProviderStatus.EXHAUSTED, ProviderStatus.STOPPED}:
            exhausted = session.model_copy(update={"status": ProviderStatus.EXHAUSTED})
            return MeetingInputEventBatch(session=exhausted, status=ProviderStatus.EXHAUSTED)
        if session.transcript_path:
            segments = self.transcripts._load_segments(Path(session.transcript_path), session.meeting_id)
            pending = segments[session.cursor :]
            events = [_segment_to_event(segment, session.live_run_id) for segment in pending]
        else:
            segments = []
            pending = []
            events = []
            if session.cursor == 0:
                events = [
                    LiveMeetingEvent(
                        event_id=f"{session.session_id}-audio-registered",
                        live_run_id=session.live_run_id,
                        meeting_id=session.meeting_id,
                        kind=LiveEventKind.MARKER,
                        text="local audio file registered; no transcript sidecar provided",
                    )
                ]
        status = ProviderStatus.EXHAUSTED
        cursor = len(segments) if session.transcript_path else 1
        updated = session.model_copy(update={"cursor": cursor, "status": status})
        return MeetingInputEventBatch(
            session=updated,
            events=events,
            transcript_segments=pending,
            status=status,
            has_more=False,
        )

    def stop(self, session: MeetingInputSession) -> None:
        session.status = ProviderStatus.STOPPED


def _segment_to_event(segment: TranscriptSegment, live_run_id: str) -> LiveMeetingEvent:
    return LiveMeetingEvent(
        event_id=f"{live_run_id}-{segment.segment_id}",
        live_run_id=live_run_id,
        meeting_id=segment.meeting_id,
        kind=LiveEventKind.TRANSCRIPT_DELTA,
        text=segment.text,
        speaker_name=segment.speaker_name,
        timestamp=segment.start_time,
        segment_id=segment.segment_id,
    )


def _required_existing_file(path: str | None, workspace: Path) -> Path:
    if not path:
        raise ValueError("source_path is required")
    resolved = _resolve(path, workspace)
    if not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    return resolved


def _optional_existing_file(path: str | None, workspace: Path) -> Path | None:
    if not path:
        return None
    resolved = _resolve(path, workspace)
    if not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    return resolved


def _resolve(path: str, workspace: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = workspace / candidate
    return candidate.resolve()


def _audio_metadata(path: Path) -> dict[str, str]:
    metadata = {"audio_file_name": path.name, "audio_file_type": path.suffix.lower().lstrip(".")}
    if path.suffix.lower() != ".wav":
        return metadata
    try:
        with wave.open(str(path), "rb") as handle:
            frames = handle.getnframes()
            rate = handle.getframerate()
            channels = handle.getnchannels()
            metadata["sample_rate_hz"] = str(rate)
            metadata["channels"] = str(channels)
            if rate:
                metadata["duration_sec"] = f"{frames / float(rate):.3f}"
    except wave.Error:
        metadata["audio_metadata_error"] = "invalid_wav"
    return metadata
