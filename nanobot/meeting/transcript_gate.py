"""Read-only real transcript/minutes availability gate."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.schemas import (
    ProviderMode,
    TranscriptGateAttempt,
    TranscriptGateReport,
    TranscriptGateSource,
)


class TranscriptGateWorkflow:
    def __init__(
        self,
        workspace: Path | str,
        adapter_factory: Callable[[str], LarkToolAdapter] | None = None,
    ) -> None:
        self.workspace = Path(workspace)
        self.adapter_factory = adapter_factory or self._adapter

    def run(
        self,
        *,
        query: str | None = None,
        start: str | None = None,
        end: str | None = None,
        provider_mode: str | ProviderMode = ProviderMode.CLI,
        limit: int = 10,
    ) -> TranscriptGateReport:
        provider = ProviderMode(provider_mode)
        adapter = self.adapter_factory(provider.value)
        adapter.execute("auth.status", {}, dry_run=False)
        search_payload = {"query": query, "start": start, "end": end}
        meetings = _items(adapter.execute("vc.search", search_payload, dry_run=False))[:limit]
        attempts: list[TranscriptGateAttempt] = []
        for meeting in meetings:
            meeting_id = str(meeting.get("meeting_id") or meeting.get("id") or "")
            if not meeting_id:
                continue
            try:
                notes = adapter.execute("vc.notes", {"meeting_id": meeting_id}, dry_run=False)
            except Exception as exc:
                attempts.append(
                    TranscriptGateAttempt(
                        meeting_id=meeting_id,
                        title=meeting.get("title") or meeting.get("topic"),
                        reason=_exception_reason(exc),
                    )
                )
                continue
            if transcript := _extract_text(notes):
                return TranscriptGateReport(
                    status="ready",
                    provider_mode=provider,
                    query=query,
                    start=start,
                    end=end,
                    visible_meeting_count=len(meetings),
                    accessible_minute_count=0,
                    readable_source=TranscriptGateSource(
                        source_type="vc.notes",
                        meeting_id=meeting_id,
                        title=str(meeting.get("title") or meeting.get("topic") or ""),
                        text_preview=transcript[:200],
                    ),
                    checked_meetings=attempts,
                    next_process_command=_next_command(query, start, end),
                )
            attempts.append(
                TranscriptGateAttempt(
                    meeting_id=meeting_id,
                    title=meeting.get("title") or meeting.get("topic"),
                    reason=_reason(notes) or "meeting has no readable transcript",
                )
            )
        minutes = _items(adapter.execute("minutes.search", search_payload, dry_run=False))
        for minute in minutes[:limit]:
            if transcript := _extract_text(minute):
                token = str(minute.get("minute_token") or minute.get("token") or minute.get("id") or "")
                return TranscriptGateReport(
                    status="ready",
                    provider_mode=provider,
                    query=query,
                    start=start,
                    end=end,
                    visible_meeting_count=len(meetings),
                    accessible_minute_count=len(minutes),
                    readable_source=TranscriptGateSource(
                        source_type="minutes.search",
                        minute_token=token or None,
                        title=str(minute.get("title") or minute.get("topic") or ""),
                        text_preview=transcript[:200],
                    ),
                    checked_meetings=attempts,
                    next_process_command=_next_command(query, start, end),
                )
        return TranscriptGateReport(
            status="blocked",
            provider_mode=provider,
            query=query,
            start=start,
            end=end,
            visible_meeting_count=len(meetings),
            accessible_minute_count=len(minutes),
            checked_meetings=attempts,
            blocker_message="没有找到可读取的飞书妙记/会议纪要文本；请提供或创建一场当前账号可读的带转写会议。",
        )

    def _adapter(self, mode: str) -> LarkToolAdapter:
        provider = ProviderMode(mode)
        if provider == ProviderMode.FAKE:
            return LarkToolAdapter.fake(self.workspace)
        if provider == ProviderMode.OAPI:
            return LarkToolAdapter.oapi(self.workspace)
        return LarkToolAdapter.cli(self.workspace)


def _items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("meetings", "items", "minutes", "notes"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    data = payload.get("data")
    if isinstance(data, dict):
        return _items(data)
    return []


def _extract_text(payload: dict[str, Any]) -> str | None:
    for key in ("transcript", "content", "text", "markdown"):
        value = payload.get(key)
        if value:
            return str(value)
    for item in _items(payload):
        if text := _extract_text(item):
            return text
    return None


def _reason(payload: dict[str, Any]) -> str | None:
    if error := payload.get("error"):
        return str(error)
    for item in _items(payload):
        if error := item.get("error"):
            return str(error)
    return None


def _exception_reason(exc: Exception) -> str:
    raw = str(exc)
    for start in [idx for idx, char in enumerate(raw) if char == "{"]:
        try:
            parsed = json.loads(raw[start:])
        except ValueError:
            continue
        if isinstance(parsed, dict):
            error = parsed.get("error")
            if isinstance(error, dict) and error.get("message"):
                return str(error["message"])
            if parsed.get("message"):
                return str(parsed["message"])
    return raw


def _next_command(query: str | None, start: str | None, end: str | None) -> str:
    parts = ["scripts/lma-real process", "--latest-ended", "--create-doc", "--create-tasks", "--dry-run"]
    if query:
        parts.extend(["--query", f'"{query}"'])
    if start:
        parts.extend(["--start", f'"{start}"'])
    if end:
        parts.extend(["--end", f'"{end}"'])
    return " ".join(parts)
