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
    metadata_path = _meetingbank_metadata_path(root)
    if metadata_path:
        records = _load_meetingbank_metadata(metadata_path)
        if records:
            return records
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json")):
        for item in _load_json_records(path):
            item.setdefault("_source_path", str(path))
            item.setdefault("_source_split", _split_from_path(path))
            records.append(item)
    for path in sorted(root.rglob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            records.append(
                {
                    "id": path.stem,
                    "title": path.stem.replace("_", " "),
                    "transcript": text,
                    "_source_path": str(path),
                    "_source_split": _split_from_path(path),
                }
            )
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
            source_split=_optional_str(_first(record, "split", "_source_split", default="unknown")),
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


def prepare_tiny10(
    raw_root: Path | str,
    out_root: Path | str,
    manifest_path: Path | str,
    *,
    limit: int = 10,
    seed: int = 20260611,
) -> list[MeetingFixture]:
    records = [record for record in load_records(raw_root) if _has_text(record)]
    records = sorted(records, key=_score_record, reverse=True)
    selected = _select_tiny_records(records, limit, seed)
    fixtures = [record_to_fixture(record, index) for index, record in enumerate(selected)]
    out = Path(out_root)
    manifest_rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        path = out / f"{fixture.fixture_id}.json"
        save_fixture(fixture, path)
        manifest_rows.append(_manifest(fixture, path, "seeded tiny10; prefer validation/test, transcript, summary, agenda metadata, diversity"))
    write_manifest(manifest_rows, manifest_path)
    return fixtures


def _turns(record: dict[str, Any]) -> list[TranscriptTurn]:
    raw = _first(record, "transcript", "transcripts", "turns", "utterances", default=[])
    if isinstance(raw, str):
        lines = _split_transcript_text(raw)
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


def _meetingbank_metadata_path(root: Path) -> Path | None:
    for path in (root / "Metadata" / "MeetingBank.json", root / "uploaded" / "Metadata" / "MeetingBank.json"):
        if path.exists():
            return path
    return None


def _load_meetingbank_metadata(path: Path) -> list[dict[str, Any]]:
    meetings = json.loads(path.read_text(encoding="utf-8"))
    split_map = _load_split_map(path.parent / "Splits")
    records: list[dict[str, Any]] = []
    if not isinstance(meetings, dict):
        return records
    for meeting_id, meeting in meetings.items():
        if not isinstance(meeting, dict):
            continue
        city = _city_from_meeting_id(str(meeting_id))
        item_info = meeting.get("itemInfo") if isinstance(meeting.get("itemInfo"), dict) else {}
        full_agenda = []
        full_summary_parts = []
        for item_id, item in item_info.items():
            if not isinstance(item, dict) or not item.get("transcripts"):
                continue
            source_id = f"{meeting_id}_{item_id}"
            split_summary = split_map.get(source_id, {})
            summary = _optional_str(item.get("Summary") or split_summary.get("summary"))
            title = _optional_str(split_summary.get("summary") or item.get("Summary") or item_id) or str(item_id)
            full_agenda.append({"title": title, "summary": summary})
            if summary:
                full_summary_parts.append(summary)
            records.append(
                {
                    "id": source_id,
                    "title": title,
                    "meeting_id": meeting_id,
                    "item_id": item_id,
                    "city": city,
                    "domain": "city_council",
                    "type": item.get("type") or "Agenda Item",
                    "transcripts": item.get("transcripts"),
                    "agenda": [{"title": title, "summary": summary}],
                    "summary": summary,
                    "duration": item.get("duration"),
                    "split": split_summary.get("split", "unknown"),
                    "_fixture_kind": "segment",
                    "_source_path": str(path),
                    "_source_split": split_summary.get("split", "unknown"),
                }
            )
        transcript = _load_full_transcript(path.parent.parent, city, meeting.get("Transcripts"))
        if transcript:
            records.append(
                {
                    "id": str(meeting_id),
                    "title": str(meeting_id).replace("_", " "),
                    "meeting_id": meeting_id,
                    "city": city,
                    "domain": "city_council",
                    "transcripts": transcript,
                    "agenda": full_agenda,
                    "summary": "\n".join(full_summary_parts[:12]) or None,
                    "duration": meeting.get("VideoDuration"),
                    "split": "unknown",
                    "_fixture_kind": "full",
                    "_source_path": str(path),
                    "_source_split": "unknown",
                }
            )
    return records


def _load_split_map(split_root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not split_root.exists():
        return rows
    for path in sorted(split_root.glob("*.json")):
        split = path.stem
        for row in _load_json_records(path):
            source_id = str(row.get("id", ""))
            if source_id:
                row["split"] = "validation" if split == "valid" else split
                rows[source_id] = row
    return rows


def _load_full_transcript(raw_root: Path, city: str, transcript_ref: Any) -> list[dict[str, Any]]:
    if isinstance(transcript_ref, list):
        return [item for item in transcript_ref if isinstance(item, dict)]
    if not isinstance(transcript_ref, str) or not transcript_ref.strip():
        return []
    candidates = [
        raw_root / "Audio&Transcripts" / city / "transcripts" / transcript_ref,
        raw_root / "Audio&Transcripts" / city.replace(" ", "") / "transcripts" / transcript_ref,
    ]
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    if path is None:
        matches = list((raw_root / "Audio&Transcripts").rglob(transcript_ref))
        path = matches[0] if matches else None
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    segments = data.get("segments") if isinstance(data, dict) else None
    if not isinstance(segments, list):
        return []
    turns: list[dict[str, Any]] = []
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        nbest = segment.get("nbest")
        best = nbest[0] if isinstance(nbest, list) and nbest and isinstance(nbest[0], dict) else {}
        text = best.get("text") or segment.get("text")
        if not text:
            continue
        start = _ticks_to_seconds(segment.get("offset"))
        duration = _ticks_to_seconds(segment.get("duration"))
        turns.append(
            {
                "text": str(text),
                "speaker": segment.get("speaker"),
                "startTime": start,
                "endTime": start + duration if start is not None and duration is not None else None,
            }
        )
    return turns


def _load_json_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    try:
        return _iter_records(json.loads(text))
    except json.JSONDecodeError:
        rows: list[dict[str, Any]] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                rows.append(item)
        return rows


def _select_tiny_records(records: list[dict[str, Any]], limit: int, seed: int) -> list[dict[str, Any]]:
    if limit != 10:
        return deterministic_sample(records, limit, seed=seed)
    segments = [record for record in records if record.get("_fixture_kind") == "segment"]
    full = [record for record in records if record.get("_fixture_kind") == "full"]
    selected = deterministic_sample(segments[: max(60, len(segments))], 6, seed=seed)
    selected.extend(deterministic_sample(full[: max(40, len(full))], 4, seed=seed + 1))
    if len(selected) < limit:
        seen = {id(record) for record in selected}
        selected.extend(record for record in deterministic_sample(records, limit, seed=seed + 2) if id(record) not in seen)
    return selected[:limit]


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


def _iter_records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []
    for key in ("meetings", "items", "data", "records"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return [data]


def _split_from_path(path: Path) -> str:
    lowered = str(path).lower()
    for split in ("validation", "valid", "test", "train"):
        if split in lowered:
            return "validation" if split == "valid" else split
    return "unknown"


def _score_record(record: dict[str, Any]) -> tuple[int, int, int, int]:
    split = str(_first(record, "split", "_source_split", default="")).lower()
    preferred_split = int(split in {"validation", "test"})
    has_summary = int(bool(_first(record, "summary", "minutes", "reference_summary", "segment_summary")))
    has_agenda = int(bool(_first(record, "agenda", "agenda_items", "items")))
    has_timing = int("start" in json.dumps(record, ensure_ascii=False).lower() or "duration" in json.dumps(record, ensure_ascii=False).lower())
    return preferred_split, has_summary, has_agenda, has_timing


def _city_from_meeting_id(meeting_id: str) -> str:
    for suffix in ("CityCouncil", "CC"):
        if suffix in meeting_id:
            return meeting_id.split(suffix, 1)[0]
    return meeting_id.split("_", 1)[0]


def _ticks_to_seconds(value: Any) -> float | None:
    try:
        return float(value) / 10_000_000
    except (TypeError, ValueError):
        return None


def _split_transcript_text(text: str, max_chars: int = 900) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) > 1:
        return lines
    normalized = " ".join(text.split())
    if not normalized:
        return []
    chunks: list[str] = []
    current = ""
    for sentence in normalized.replace("? ", "?\n").replace("! ", "!\n").replace(". ", ".\n").splitlines():
        sentence = sentence.strip()
        if not sentence:
            continue
        if current and len(current) + len(sentence) + 1 > max_chars:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    if not chunks:
        chunks = [normalized[index : index + max_chars] for index in range(0, len(normalized), max_chars)]
    return chunks


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
