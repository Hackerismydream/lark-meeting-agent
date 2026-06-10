"""Transcript normalization."""

from __future__ import annotations

import json
import re
from typing import Any

from nanobot.meeting.errors import TranscriptNormalizationError
from nanobot.meeting.schemas import TranscriptSegment

_LINE_RE = re.compile(
    r"^\s*(?:\[(?P<ts>[^\]]+)\]\s*)?(?:(?P<speaker>[^:：\n]{1,40})[:：]\s*)?(?P<text>.+?)\s*$"
)


class TranscriptNormalizer:
    """Normalize plain text, JSON, or markdown-ish transcript content."""

    def normalize_text(self, meeting_id: str, text: str) -> list[TranscriptSegment]:
        if not text or not text.strip():
            raise TranscriptNormalizationError("transcript is empty")

        chunks = self._split_text(text)
        segments: list[TranscriptSegment] = []
        for index, raw in enumerate(chunks, start=1):
            match = _LINE_RE.match(raw)
            if not match:
                raise TranscriptNormalizationError(f"cannot parse transcript line: {raw!r}")
            body = (match.group("text") or "").strip()
            if not body:
                continue
            segments.append(
                TranscriptSegment(
                    segment_id=f"seg-{index:04d}",
                    meeting_id=meeting_id,
                    speaker_name=self._clean_speaker(match.group("speaker")),
                    start_time=self._clean(match.group("ts")),
                    text=body,
                )
            )
        if not segments:
            raise TranscriptNormalizationError("transcript has no usable segments")
        return segments

    def normalize_json(self, meeting_id: str, value: Any) -> list[TranscriptSegment]:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise TranscriptNormalizationError("invalid transcript JSON") from exc
        if isinstance(value, dict):
            if "transcript" in value:
                return self.normalize_text(meeting_id, str(value["transcript"]))
            if "segments" in value:
                value = value["segments"]
        if not isinstance(value, list):
            raise TranscriptNormalizationError("JSON transcript must be a list or transcript object")

        segments: list[TranscriptSegment] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise TranscriptNormalizationError("JSON transcript segment must be an object")
            text = str(item.get("text") or item.get("content") or "").strip()
            if not text:
                raise TranscriptNormalizationError("JSON transcript segment text is empty")
            segments.append(
                TranscriptSegment(
                    segment_id=str(item.get("segment_id") or f"seg-{index:04d}"),
                    meeting_id=meeting_id,
                    speaker_name=self._clean(item.get("speaker_name") or item.get("speaker")),
                    speaker_id=self._clean(item.get("speaker_id")),
                    start_time=self._clean(item.get("start_time") or item.get("timestamp")),
                    end_time=self._clean(item.get("end_time")),
                    text=text,
                )
            )
        return segments

    @staticmethod
    def _split_text(text: str) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) > 1:
            return lines
        return [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()]

    @staticmethod
    def _clean(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @classmethod
    def _clean_speaker(cls, value: Any) -> str | None:
        speaker = cls._clean(value)
        if not speaker:
            return None
        if any(marker in speaker for marker in ("。", "，", " ", "\t")) and len(speaker) > 12:
            return None
        return speaker
