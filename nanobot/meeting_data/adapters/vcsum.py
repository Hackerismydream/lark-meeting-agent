"""VCSum adapter."""

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

DOWNLOAD_INSTRUCTIONS = """VCSum raw data is missing.
Run:
  git clone --depth 1 https://github.com/hahahawu/VCSum data/raw/vcsum
"""


def load_records(raw_root: Path | str) -> list[dict[str, Any]]:
    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(DOWNLOAD_INSTRUCTIONS)
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json")) + sorted(root.rglob("*.jsonl")):
        if path.suffix == ".jsonl":
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    item = json.loads(line)
                    if isinstance(item, dict):
                        item.setdefault("_source_path", str(path))
                        records.append(item)
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            values = data if isinstance(data, list) else [data]
            for item in values:
                if isinstance(item, dict):
                    item.setdefault("_source_path", str(path))
                    records.append(item)
    if not records:
        raise FileNotFoundError(DOWNLOAD_INSTRUCTIONS)
    return records


def record_to_fixture(record: dict[str, Any], index: int = 0) -> MeetingFixture:
    source_id = str(_first(record, "id", "meeting_id", "source_id", default=f"vcsum-{index:04d}"))
    turns = _turns(record)
    agenda = _agenda(record, turns)
    segments = _segments(record, turns, agenda)
    highlights = _highlight_turn_ids(record, turns)
    return MeetingFixture(
        fixture_id=f"vcsum-{source_id}",
        dataset=DatasetName.VCSUM,
        meta=MeetingMeta(
            title=str(_first(record, "title", "headline", default=f"VCSum {source_id}")),
            language="zh",
            domain="Chinese meeting",
        ),
        provenance=Provenance(
            source_id=source_id,
            source_path=_optional_str(record.get("_source_path")),
            source_split=_optional_str(_first(record, "split", default="unknown")),
            source_domain="Chinese meeting",
            license="VCSum research dataset",
            url="https://github.com/hahahawu/VCSum",
            raw_available=True,
        ),
        agenda=agenda,
        transcript_turns=turns,
        topic_segments=segments,
        expected=ExpectedArtifacts(
            overall_summary=_optional_str(_first(record, "summary", "overall_summary")),
            segment_summaries={segment.segment_id: segment.summary or "" for segment in segments if segment.summary},
            salient_turn_ids=highlights,
        ),
    )


def prepare_tiny10(raw_root: Path | str, out_root: Path | str, manifest_path: Path | str) -> list[MeetingFixture]:
    records = [record for record in load_records(raw_root) if _first(record, "context", "transcript")]
    selected = deterministic_sample(records, 10)
    fixtures = [record_to_fixture(record, index) for index, record in enumerate(selected)]
    out = Path(out_root)
    rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        path = out / f"{fixture.fixture_id}.json"
        save_fixture(fixture, path)
        rows.append(_manifest(fixture, path, "deterministic tiny10 for Chinese summary/topic/evidence cases"))
    write_manifest(rows, manifest_path)
    return fixtures


def _turns(record: dict[str, Any]) -> list[TranscriptTurn]:
    context = _first(record, "context", "transcript", "turns", default=[])
    speakers = record.get("speaker") or record.get("speakers") or []
    if isinstance(context, str):
        parts = [part.strip() for part in context.splitlines() if part.strip()]
    elif isinstance(context, list):
        parts = [str(part.get("text") if isinstance(part, dict) else part).strip() for part in context]
    else:
        parts = []
    turns = []
    for index, text in enumerate(parts):
        if not text:
            continue
        speaker = None
        if isinstance(speakers, list) and index < len(speakers):
            speaker = str(speakers[index])
        elif isinstance(context, list) and isinstance(context[index], dict):
            speaker = _optional_str(_first(context[index], "speaker", "speaker_name"))
        turns.append(TranscriptTurn(turn_id=f"turn-{index + 1:04d}", speaker=speaker, text=text, start_sec=float(index * 10)))
    if not turns:
        raise ValueError("VCSum record has no context text")
    return turns


def _agenda(record: dict[str, Any], turns: list[TranscriptTurn]) -> list[AgendaItem]:
    raw = _first(record, "agenda", "headlines", default=[])
    if isinstance(raw, str):
        raw = [raw]
    items: list[AgendaItem] = []
    if isinstance(raw, list):
        for index, item in enumerate(raw):
            title = item.get("title") if isinstance(item, dict) else item
            if str(title).strip():
                items.append(AgendaItem(agenda_id=f"agenda-{index + 1:03d}", title=str(title)))
    if not items:
        items.append(AgendaItem(agenda_id="agenda-001", title="会议讨论", start_turn_id=turns[0].turn_id, end_turn_id=turns[-1].turn_id))
    return items


def _segments(record: dict[str, Any], turns: list[TranscriptTurn], agenda: list[AgendaItem]) -> list[TopicSegment]:
    eos = record.get("eos_index") or record.get("eos_indices") or []
    discussions = record.get("discussion") or record.get("segment_summaries") or []
    if isinstance(discussions, str):
        discussions = [discussions]
    boundaries = [int(value) for value in eos] if isinstance(eos, list) and eos else [len(turns) - 1]
    segments: list[TopicSegment] = []
    start = 0
    for index, end in enumerate(boundaries):
        end = min(max(end, start), len(turns) - 1)
        agenda_item = agenda[min(index, len(agenda) - 1)]
        summary = str(discussions[index]) if isinstance(discussions, list) and index < len(discussions) else None
        segments.append(
            TopicSegment(
                segment_id=f"topic-{index + 1:03d}",
                headline=agenda_item.title,
                start_turn_id=turns[start].turn_id,
                end_turn_id=turns[end].turn_id,
                summary=summary,
                agenda_id=agenda_item.agenda_id,
            )
        )
        start = min(end + 1, len(turns) - 1)
    return segments


def _highlight_turn_ids(record: dict[str, Any], turns: list[TranscriptTurn]) -> list[str]:
    highlights = record.get("highlights") or record.get("salient_sentences") or []
    if not isinstance(highlights, list):
        return []
    ids: list[str] = []
    for value in highlights:
        if isinstance(value, int) and 0 <= value < len(turns):
            ids.append(turns[value].turn_id)
        elif isinstance(value, str):
            for turn in turns:
                if value and value in turn.text:
                    ids.append(turn.turn_id)
                    break
    return list(dict.fromkeys(ids))


def _first(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return default


def _optional_str(value: Any) -> str | None:
    return None if value in (None, "") else str(value)


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
