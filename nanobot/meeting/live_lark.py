"""Lark live meeting listener workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import Field

from nanobot.meeting.errors import ToolExecutionError
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


class LiveSmokeResult(MeetingBaseModel):
    status: str
    provider_mode: ProviderMode
    meeting_number: str | None = None
    meeting_id: str | None = None
    live_run_id: str | None = None
    page_token: str | None = None
    event_count: int = 0
    qa_sufficient: bool | None = None
    failure_class: str | None = None
    error: str | None = None
    raw_event_shape_path: str | None = None


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
        if not _valid_meeting_number(meeting_number):
            raise ToolExecutionError("meeting_number must be exactly 9 digits")
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
        session = LiveLarkSession(live_run_id=live_run_id, meeting_id=meeting_id, page_token=page_token)
        return self.ingest_raw_events(session, raw)

    def ingest_raw_events(self, session: LiveLarkSession, raw: dict[str, Any]) -> LiveLarkPollResult:
        events = self.convert_events(raw, session=session)
        for event in events:
            self.live.ingest(event)
        state = self.live.memory.load_live_state(session.live_run_id)
        state.page_token = _page_token(raw) or session.page_token
        state.has_more = bool(raw.get("has_more") or raw.get("data", {}).get("has_more"))
        self.live.memory.save_live_state(state)
        updated_session = session.model_copy(update={"page_token": state.page_token})
        converted_count = sum(1 for event in events if event.event_id in state.seen_event_ids)
        return LiveLarkPollResult(
            session=updated_session,
            state=state,
            raw=raw,
            page_token=state.page_token,
            converted_event_count=converted_count,
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

    def live_smoke(
        self,
        *,
        meeting_number: str | None,
        approve_visible_join: bool = False,
        approve_visible_leave: bool = False,
        export_raw_event_shapes: Path | str | None = None,
    ) -> LiveSmokeResult:
        if not meeting_number:
            return LiveSmokeResult(
                status="missing_meeting_number",
                provider_mode=self.provider_mode,
                error="--meeting-number is required for live-smoke",
            )
        if not approve_visible_join or not approve_visible_leave:
            return LiveSmokeResult(
                status="dry_run",
                provider_mode=self.provider_mode,
                meeting_number=meeting_number,
                error="real smoke not executed; pass --approve-visible-join and --approve-visible-leave to visibly join and leave",
            )
        try:
            session = self.join(
                meeting_number=meeting_number,
                dry_run=False,
                approval_status=ApprovalStatus.APPROVED,
            )
            poll = self.poll(session.meeting_id, live_run_id=session.live_run_id)
            answer = self.qa(session.live_run_id, "目前有哪些结论和待办？")
            raw_path = None
            if export_raw_event_shapes:
                raw_path = str(write_sanitized_event_shapes(poll.raw, export_raw_event_shapes, self.adapter))
            self.leave(session.meeting_id, dry_run=False, approval_status=ApprovalStatus.APPROVED)
            status = "completed" if poll.converted_event_count else "blocked"
            failure_class = None if poll.converted_event_count else "no_events"
            return LiveSmokeResult(
                status=status,
                provider_mode=self.provider_mode,
                meeting_number=meeting_number,
                meeting_id=session.meeting_id,
                live_run_id=session.live_run_id,
                page_token=poll.page_token,
                event_count=poll.converted_event_count,
                qa_sufficient=answer.sufficient,
                failure_class=failure_class,
                raw_event_shape_path=raw_path,
            )
        except Exception as exc:
            return LiveSmokeResult(
                status="blocked",
                provider_mode=self.provider_mode,
                meeting_number=meeting_number,
                failure_class=classify_live_smoke_error(str(exc)),
                error=self.adapter.redact(str(exc)),
            )

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
    if event_type in {"transcript_received", "chat_received", "message_received"}:
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
    token = raw.get("next_page_token") or raw.get("page_token") or raw.get("data", {}).get("next_page_token") or raw.get("data", {}).get("page_token")
    return str(token) if token else None


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _valid_meeting_number(value: str) -> bool:
    return len(value) == 9 and value.isdigit()


def classify_live_smoke_error(message: str) -> str:
    normalized = message.lower()
    if "permission" in normalized or "scope" in normalized or "unauthorized" in normalized:
        return "permission"
    if "errnotingray" in normalized or "gray" in normalized or "early" in normalized:
        return "gray"
    if "not in meeting" in normalized or "bot is not in meeting" in normalized:
        return "not_in_meeting"
    if "meeting_status_meeting_end" in normalized or "meeting ended" in normalized or "meeting_end" in normalized:
        return "meeting_ended"
    if "page_token" in normalized or "page token" in normalized:
        return "page_token_issue"
    if "malformed" in normalized or "unknown event" in normalized or "json" in normalized:
        return "unknown_event_shape"
    return "unknown_error"


def write_sanitized_event_shapes(raw: dict[str, Any], output_path: Path | str, adapter: LarkToolAdapter) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    events = raw.get("events") or raw.get("data", {}).get("events") or []
    shapes = []
    for event in events:
        if not isinstance(event, dict):
            continue
        shapes.append(_shape(event))
    sanitized = json_safe_redact({"events": shapes, "has_more": raw.get("has_more"), "page_token_present": bool(_page_token(raw))}, adapter)
    output.write_text(sanitized)
    return output


def json_safe_redact(value: dict[str, Any], adapter: LarkToolAdapter) -> str:
    import json

    return adapter.redact(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def _shape(value: dict[str, Any]) -> dict[str, Any]:
    shape: dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(item, dict):
            shape[key] = _shape(item)
        elif isinstance(item, list):
            shape[key] = ["list"]
        elif key in {"event_type", "type"}:
            shape[key] = item
        elif key in {"event_id", "id", "segment_id"}:
            shape[key] = "<id>"
        else:
            shape[key] = type(item).__name__
    return shape
