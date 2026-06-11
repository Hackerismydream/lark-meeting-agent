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
    for path in sorted(root.rglob("*.json")) + sorted(root.rglob("*.jsonl")) + sorted(root.rglob("*.txt")):
        if path.suffix in {".jsonl", ".txt"}:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(item, dict):
                        item.setdefault("_source_path", str(path))
                        item.setdefault("_source_split", _split_from_path(path))
                        records.append(item)
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for item in _iter_records(data):
                item.setdefault("_source_path", str(path))
                item.setdefault("_source_split", _split_from_path(path))
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
            source_split=_optional_str(_first(record, "split", "_source_split", default="unknown")),
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


def prepare_tiny10(
    raw_root: Path | str,
    out_root: Path | str,
    manifest_path: Path | str,
    *,
    limit: int = 10,
    seed: int = 20260611,
) -> list[MeetingFixture]:
    records = [record for record in load_records(raw_root) if _first(record, "context", "transcript")]
    records = sorted(records, key=_score_record, reverse=True)
    selected = deterministic_sample(records, limit, seed=seed)
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
        parts = _flatten_text_parts(context)
    else:
        parts = []
    turns = []
    for index, text in enumerate(parts):
        if not text:
            continue
        speaker = None
        if isinstance(speakers, list) and index < len(speakers):
            speaker = str(speakers[index])
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
    context = _first(record, "context", "transcript", default=[])
    grouped_lengths = _grouped_lengths(context)
    if grouped_lengths:
        boundaries = []
        total = 0
        for length in grouped_lengths:
            total += length
            boundaries.append(total - 1)
    else:
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
    flags = _flatten_ints(highlights)
    if flags:
        return [turns[index].turn_id for index, value in enumerate(flags[: len(turns)]) if value == 1]
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


def _iter_records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("data", "items", "records", "meetings"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [data]
    return []


def _score_record(record: dict[str, Any]) -> tuple[int, int, int, int, int]:
    has_speaker = int(bool(record.get("speaker") or record.get("speakers")))
    has_eos = int(bool(record.get("eos_index") or record.get("eos_indices")))
    has_summary = int(bool(_first(record, "summary", "overall_summary")))
    has_discussion = int(bool(record.get("discussion") or record.get("segment_summaries")))
    length = len(_flatten_text_parts(_first(record, "context", "transcript", default=[])))
    return has_summary, has_eos, has_discussion, has_speaker, length


def _flatten_text_parts(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, dict):
        text = value.get("text") or value.get("content") or value.get("utterance")
        return [str(text).strip()] if text else []
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            parts.extend(_flatten_text_parts(item))
        return [part for part in parts if part]
    return []


def _grouped_lengths(value: Any) -> list[int]:
    if not isinstance(value, list) or not value:
        return []
    lengths: list[int] = []
    for item in value:
        if isinstance(item, list):
            length = len(_flatten_text_parts(item))
            if length:
                lengths.append(length)
    return lengths


def _flatten_ints(value: Any) -> list[int]:
    if isinstance(value, int):
        return [value]
    if isinstance(value, list):
        values: list[int] = []
        for item in value:
            values.extend(_flatten_ints(item))
        return values
    return []


def _split_from_path(path: Path) -> str:
    lowered = str(path).lower()
    for split in ("dev", "test", "train"):
        if split in lowered:
            return "validation" if split == "dev" else split
    return "unknown"


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
