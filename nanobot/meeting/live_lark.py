"""Lark live meeting listener workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import Field

from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.live import LiveMeetingWorkflow
from nanobot.meeting.schemas import (
    ApprovalStatus,
    LiveEventKind,
    LiveMeetingEvent,
    LiveMeetingState,
    MeetingBaseModel,
    ProviderMode,
)


class LiveLarkSession(MeetingBaseModel):
    live_run_id: str
    meeting_id: str
    meeting_number: str | None = None
    title: str = "live meeting"
    page_token: str | None = None
    joined_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LiveLarkPollResult(MeetingBaseModel):
    session: LiveLarkSession
    state: LiveMeetingState
    raw: dict[str, Any] = Field(default_factory=dict)
    page_token: str | None = None
    converted_event_count: int = 0


class LiveLarkMeetingWorkflow:
    def __init__(self, workspace: Path | str, provider_mode: ProviderMode | str = ProviderMode.FAKE) -> None:
        self.workspace = Path(workspace)
        self.provider_mode = ProviderMode(provider_mode)
        self.live = LiveMeetingWorkflow(self.workspace)
        self.adapter = self._adapter()

    def join(
        self,
        *,
        meeting_number: str,
        password: str | None = None,
        dry_run: bool = True,
        approval_status: ApprovalStatus | str | None = None,
        title: str = "live meeting",
    ) -> LiveLarkSession:
        payload = {"meeting_number": meeting_number}
        if password:
            payload["password"] = password
        result = self.adapter.execute(
            "vc.meeting.join",
            payload,
            dry_run=dry_run,
            approval_status=approval_status,
        )
        meeting = _as_dict(result.get("meeting") or result.get("data", {}).get("meeting") or result.get("data") or {})
        meeting_id = str(meeting.get("id") or meeting.get("meeting_id") or f"dry-run-{meeting_number}")
        session = self.start_local_session(
            meeting_id=meeting_id,
            meeting_number=meeting_number,
            title=str(meeting.get("topic") or meeting.get("title") or title),
        )
        return session

    def start_local_session(
        self,
        *,
        meeting_id: str,
        meeting_number: str | None = None,
        title: str = "live meeting",
    ) -> LiveLarkSession:
        state = self.live.start(meeting_id, title)
        return LiveLarkSession(
            live_run_id=state.live_run_id,
            meeting_id=meeting_id,
            meeting_number=meeting_number,
            title=title,
        )

    def poll(
        self,
        meeting_id: str,
        *,
        live_run_id: str,
        page_token: str | None = None,
        page_all: bool = True,
        start: str | None = None,
        end: str | None = None,
    ) -> LiveLarkPollResult:
        payload: dict[str, Any] = {"meeting_id": meeting_id, "page_all": page_all}
        if page_token:
            payload["page_token"] = page_token
        if start:
            payload["start"] = start
        if end:
            payload["end"] = end
        raw = self.adapter.execute("vc.meeting.events", payload)
        session = LiveLarkSession(
            live_run_id=live_run_id,
            meeting_id=meeting_id,
            page_token=_page_token(raw),
        )
        events = self.convert_events(raw, session=session)
        state: LiveMeetingState | None = None
        for event in events:
            state = self.live.ingest(event)
        if state is None:
            state = self.live.memory.load_live_state(live_run_id)
        return LiveLarkPollResult(
            session=session,
            state=state,
            raw=raw,
            page_token=session.page_token,
            converted_event_count=len(events),
        )

    def leave(
        self,
        meeting_id: str,
        *,
        dry_run: bool = True,
        approval_status: ApprovalStatus | str | None = None,
    ) -> dict[str, Any]:
        return self.adapter.execute(
            "vc.meeting.leave",
            {"meeting_id": meeting_id},
            dry_run=dry_run,
            approval_status=approval_status,
        )

    def qa(self, live_run_id: str, question: str):
        return self.live.qa(live_run_id, question)

    def convert_events(self, raw: dict[str, Any], *, session: LiveLarkSession) -> list[LiveMeetingEvent]:
        events = raw.get("events") or raw.get("data", {}).get("events") or raw.get("items") or raw.get("data", {}).get("items") or []
        converted: list[LiveMeetingEvent] = []
        for index, item in enumerate(events, start=1):
            if not isinstance(item, dict):
                continue
            event_type = str(item.get("event_type") or item.get("type") or "")
            text = _event_text(item)
            kind = _event_kind(event_type)
            if kind in {LiveEventKind.TRANSCRIPT_DELTA, LiveEventKind.MARKER} and not text:
                continue
            converted.append(
                LiveMeetingEvent(
                    event_id=str(item.get("event_id") or item.get("id") or f"lark-event-{index}"),
                    live_run_id=session.live_run_id,
                    meeting_id=session.meeting_id,
                    kind=kind,
                    text=text,
                    speaker_name=_speaker_name(item),
                    timestamp=str(item.get("start_time") or item.get("timestamp") or item.get("time") or "")
                    or None,
                    segment_id=str(item.get("segment_id") or f"lark-{index:04d}"),
                )
            )
        return converted

    def _adapter(self) -> LarkToolAdapter:
        if self.provider_mode == ProviderMode.FAKE:
            return LarkToolAdapter.fake(self.workspace)
        if self.provider_mode == ProviderMode.CLI:
            return LarkToolAdapter.cli(self.workspace)
        if self.provider_mode == ProviderMode.OAPI:
            return LarkToolAdapter.oapi(self.workspace)
        raise ValueError(f"unsupported provider mode: {self.provider_mode}")


def _event_kind(event_type: str) -> LiveEventKind:
    if event_type == "transcript_received":
        return LiveEventKind.TRANSCRIPT_DELTA
    if event_type == "participant_joined":
        return LiveEventKind.PARTICIPANT_JOIN
    if event_type == "participant_left":
        return LiveEventKind.PARTICIPANT_LEAVE
    return LiveEventKind.MARKER


def _event_text(item: dict[str, Any]) -> str | None:
    for key in ("text", "content"):
        if value := item.get(key):
            return str(value)
    for container_key in ("transcript", "message", "chat", "data"):
        container = item.get(container_key)
        if isinstance(container, dict):
            for text_key in ("text", "content", "plain_text"):
                if value := container.get(text_key):
                    return str(value)
    return None


def _speaker_name(item: dict[str, Any]) -> str | None:
    for key in ("speaker_name", "sender_name", "user_name"):
        if value := item.get(key):
            return str(value)
    for container_key in ("speaker", "sender", "user", "participant"):
        container = item.get(container_key)
        if isinstance(container, dict):
            for name_key in ("name", "display_name", "nickname"):
                if value := container.get(name_key):
                    return str(value)
    return None


def _page_token(raw: dict[str, Any]) -> str | None:
    token = raw.get("page_token") or raw.get("next_page_token") or raw.get("data", {}).get("page_token")
    return str(token) if token else None


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
