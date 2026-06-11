"""MeetingBank adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nanobot.meeting_data.fixture_store import save_fixture
from nanobot.meeting_data.sampling import deterministic_sample, write_manifest
from nanobot.meeting_data.schemas import (
    AgendaItem,
    DatasetName,
    ExpectedArtifacts,
    MeetingFixture,
    MeetingMeta,
    Provenance,
    TopicSegment,
    TranscriptTurn,
)

DOWNLOAD_INSTRUCTIONS = """MeetingBank raw data is missing.
Run:
  mkdir -p data/raw/meetingbank
  curl -L -o data/raw/meetingbank/MeetingBank.zip "https://zenodo.org/records/7989108/files/MeetingBank.zip?download=1"
  unzip data/raw/meetingbank/MeetingBank.zip -d data/raw/meetingbank
"""


def load_records(raw_root: Path | str) -> list[dict[str, Any]]:
    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(DOWNLOAD_INSTRUCTIONS)
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item.setdefault("_source_path", str(path))
                    records.append(item)
        elif isinstance(data, dict):
            data.setdefault("_source_path", str(path))
            records.append(data)
    if not records:
        raise FileNotFoundError(DOWNLOAD_INSTRUCTIONS)
    return records


def record_to_fixture(record: dict[str, Any], index: int = 0) -> MeetingFixture:
    source_id = str(_first(record, "id", "meeting_id", "source_id") or f"meetingbank-{index:04d}")
    turns = _turns(record)
    agenda = _agenda(record, turns)
    segments = _segments(record, turns, agenda)
    summary = str(_first(record, "summary", "minutes", "reference_summary", default="")).strip() or None
    return MeetingFixture(
        fixture_id=f"meetingbank-{source_id}",
        dataset=DatasetName.MEETINGBANK,
        meta=MeetingMeta(
            title=str(_first(record, "title", "meeting_title", default=f"MeetingBank {source_id}")),
            language="en",
            domain=str(_first(record, "domain", "city", "agency", default="city_council")),
            city=_optional_str(_first(record, "city")),
            agency=_optional_str(_first(record, "agency")),
            meeting_type=_optional_str(_first(record, "type", "meeting_type")),
        ),
        provenance=Provenance(
            source_id=source_id,
            source_path=_optional_str(record.get("_source_path")),
            source_split=_optional_str(_first(record, "split", default="unknown")),
            source_domain=_optional_str(_first(record, "domain", "city", "agency", default="city_council")),
            license=_optional_str(_first(record, "license", default="MeetingBank public corpus")),
            url="https://meetingbank.github.io/",
            raw_available=True,
        ),
        agenda=agenda,
        transcript_turns=turns,
        topic_segments=segments,
        expected=ExpectedArtifacts(
            overall_summary=summary,
            segment_summaries={segment.segment_id: segment.summary or "" for segment in segments if segment.summary},
        ),
    )


def prepare_tiny10(raw_root: Path | str, out_root: Path | str, manifest_path: Path | str) -> list[MeetingFixture]:
    records = [record for record in load_records(raw_root) if _has_text(record)]
    selected = deterministic_sample(records, 10)
    fixtures = [record_to_fixture(record, index) for index, record in enumerate(selected)]
    out = Path(out_root)
    manifest_rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        path = out / f"{fixture.fixture_id}.json"
        save_fixture(fixture, path)
        manifest_rows.append(_manifest(fixture, path, "deterministic tiny10; prefer non-empty transcript and summary"))
    write_manifest(manifest_rows, manifest_path)
    return fixtures


def _turns(record: dict[str, Any]) -> list[TranscriptTurn]:
    raw = _first(record, "transcript", "transcripts", "turns", "utterances", default=[])
    if isinstance(raw, str):
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        return [
            TranscriptTurn(turn_id=f"turn-{index + 1:04d}", speaker=None, text=line, start_sec=float(index * 10))
            for index, line in enumerate(lines)
        ]
    turns: list[TranscriptTurn] = []
    if isinstance(raw, list):
        for index, item in enumerate(raw):
            if isinstance(item, str):
                text = item
                speaker = None
                start = None
                end = None
            elif isinstance(item, dict):
                text = str(_first(item, "text", "content", "utterance", default=""))
                speaker = _optional_str(_first(item, "speaker", "speaker_name", "name"))
                start = _float_or_none(_first(item, "start_sec", "start", "start_time"))
                end = _float_or_none(_first(item, "end_sec", "end", "end_time"))
            else:
                continue
            if text.strip():
                turns.append(
                    TranscriptTurn(
                        turn_id=f"turn-{index + 1:04d}",
                        speaker=speaker,
                        text=text,
                        start_sec=start,
                        end_sec=end,
                    )
                )
    if not turns:
        raise ValueError("MeetingBank record has no transcript text")
    return turns


def _agenda(record: dict[str, Any], turns: list[TranscriptTurn]) -> list[AgendaItem]:
    raw = _first(record, "agenda", "agenda_items", "items", default=[])
    items: list[AgendaItem] = []
    if isinstance(raw, list):
        for index, item in enumerate(raw):
            if isinstance(item, str):
                title = item
                summary = None
            elif isinstance(item, dict):
                title = str(_first(item, "title", "name", "item", default=f"Agenda {index + 1}"))
                summary = _optional_str(_first(item, "summary", "description"))
            else:
                continue
            items.append(AgendaItem(agenda_id=f"agenda-{index + 1:03d}", title=title, summary=summary))
    if not items:
        items.append(
            AgendaItem(
                agenda_id="agenda-001",
                title=str(_first(record, "title", default="Meeting discussion")),
                start_turn_id=turns[0].turn_id,
                end_turn_id=turns[-1].turn_id,
            )
        )
    return items


def _segments(record: dict[str, Any], turns: list[TranscriptTurn], agenda: list[AgendaItem]) -> list[TopicSegment]:
    summary = _optional_str(_first(record, "segment_summary", "summary", "minutes"))
    return [
        TopicSegment(
            segment_id="segment-001",
            headline=agenda[0].title if agenda else "Meeting discussion",
            start_turn_id=turns[0].turn_id,
            end_turn_id=turns[-1].turn_id,
            summary=summary,
            agenda_id=agenda[0].agenda_id if agenda else None,
        )
    ]


def _first(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return default


def _optional_str(value: Any) -> str | None:
    return None if value in (None, "") else str(value)


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _has_text(record: dict[str, Any]) -> bool:
    value = _first(record, "transcript", "transcripts", "turns", "utterances", default=None)
    return bool(value)


def _manifest(fixture: MeetingFixture, path: Path, reason: str) -> dict[str, Any]:
    return {
        "fixture_id": fixture.fixture_id,
        "dataset": fixture.dataset.value,
        "source_id": fixture.provenance.source_id,
        "source_split": fixture.provenance.source_split or "unknown",
        "source_domain": fixture.provenance.source_domain or "unknown",
        "source_path": fixture.provenance.source_path or "",
        "selected_reason": reason,
        "license": fixture.provenance.license or "",
        "processed_path": str(path),
        "raw_available": fixture.provenance.raw_available,
    }
