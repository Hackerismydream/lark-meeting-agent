"""QMSum adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nanobot.meeting_data.fixture_store import save_fixture
from nanobot.meeting_data.sampling import stratified_sample, write_manifest
from nanobot.meeting_data.schemas import (
    DatasetName,
    ExpectedArtifacts,
    MeetingFixture,
    MeetingMeta,
    MeetingQuery,
    Provenance,
    TopicSegment,
    TranscriptTurn,
)

DOWNLOAD_INSTRUCTIONS = """QMSum raw data is missing.
Run:
  git clone --depth 1 https://github.com/Yale-LILY/QMSum data/raw/qmsum
"""


def load_records(raw_root: Path | str) -> list[dict[str, Any]]:
    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(DOWNLOAD_INSTRUCTIONS)
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in _iter_records(data):
            item.setdefault("_source_path", str(path))
            item.setdefault("_source_domain", _domain_from_path(path))
            item.setdefault("_source_split", _split_from_path(path))
            records.append(item)
    if not records:
        raise FileNotFoundError(DOWNLOAD_INSTRUCTIONS)
    return records


def record_to_fixture(record: dict[str, Any], index: int = 0) -> MeetingFixture:
    source_id = str(_first(record, "id", "meeting_id", "file_name", default=f"qmsum-{index:04d}"))
    turns = _turns(record)
    topics = _topics(record, turns)
    queries = _queries(record, turns)
    domain = _domain(record, source_id)
    return MeetingFixture(
        fixture_id=f"qmsum-{source_id}",
        dataset=DatasetName.QMSUM,
        meta=MeetingMeta(title=str(_first(record, "title", default=f"QMSum {source_id}")), language="en", domain=domain),
        provenance=Provenance(
            source_id=source_id,
            source_path=_optional_str(record.get("_source_path")),
            source_split=_optional_str(_first(record, "split", "_source_split", default="unknown")),
            source_domain=domain,
            license="QMSum research dataset",
            url="https://github.com/Yale-LILY/QMSum",
            raw_available=True,
        ),
        transcript_turns=turns,
        topic_segments=topics,
        queries=queries,
        expected=ExpectedArtifacts(),
    )


def prepare_tiny10(
    raw_root: Path | str,
    out_root: Path | str,
    manifest_path: Path | str,
    *,
    limit: int = 10,
    seed: int = 20260611,
) -> list[MeetingFixture]:
    fixtures = [record_to_fixture(record, index) for index, record in enumerate(load_records(raw_root))]
    fixtures = [fixture for fixture in fixtures if fixture.queries]
    fixtures = sorted(fixtures, key=_score_fixture, reverse=True)
    selected = stratified_sample(
        fixtures,
        lambda fixture: fixture.meta.domain or "Committee",
        {"Product": 4, "Academic": 3, "Committee": 3},
        seed=seed,
    )
    if len(selected) < limit:
        selected.extend([fixture for fixture in fixtures if fixture not in selected][: limit - len(selected)])
    out = Path(out_root)
    rows: list[dict[str, Any]] = []
    for fixture in selected[:limit]:
        path = out / f"{fixture.fixture_id}.json"
        save_fixture(fixture, path)
        rows.append(_manifest(fixture, path, "deterministic stratified tiny10 with answer-bearing queries"))
    write_manifest(rows, manifest_path)
    return selected[:limit]


def _turns(record: dict[str, Any]) -> list[TranscriptTurn]:
    raw = _first(record, "meeting_transcripts", "transcript", "turns", default=[])
    turns: list[TranscriptTurn] = []
    for index, item in enumerate(raw if isinstance(raw, list) else []):
        if isinstance(item, str):
            speaker = None
            text = item
        elif isinstance(item, dict):
            speaker = _optional_str(_first(item, "speaker", "speaker_name"))
            text = str(_first(item, "content", "text", "utterance", default=""))
        else:
            continue
        if text.strip():
            turns.append(TranscriptTurn(turn_id=f"turn-{index + 1:04d}", speaker=speaker, text=text, start_sec=float(index * 10)))
    if not turns and isinstance(raw, str):
        turns = [
            TranscriptTurn(turn_id=f"turn-{index + 1:04d}", text=line, start_sec=float(index * 10))
            for index, line in enumerate(raw.splitlines())
            if line.strip()
        ]
    if not turns:
        raise ValueError("QMSum record has no transcript turns")
    return turns


def _topics(record: dict[str, Any], turns: list[TranscriptTurn]) -> list[TopicSegment]:
    raw = _first(record, "topic_list", "topics", default=[])
    segments: list[TopicSegment] = []
    if isinstance(raw, list):
        for index, item in enumerate(raw):
            if isinstance(item, str):
                headline = item
            elif isinstance(item, dict):
                headline = str(_first(item, "topic", "headline", "title", default=f"Topic {index + 1}"))
            else:
                continue
            start = turns[min(index, len(turns) - 1)].turn_id
            end = turns[min(index + 1, len(turns) - 1)].turn_id
            segments.append(TopicSegment(segment_id=f"topic-{index + 1:03d}", headline=headline, start_turn_id=start, end_turn_id=end))
    return segments


def _queries(record: dict[str, Any], turns: list[TranscriptTurn]) -> list[MeetingQuery]:
    raw_queries = []
    for key in ("general_query_list", "specific_query_list", "queries"):
        value = record.get(key)
        if isinstance(value, list):
            query_type = "general" if key.startswith("general") else "specific"
            raw_queries.extend((query_type, item) for item in value)
    queries: list[MeetingQuery] = []
    for index, (query_type, item) in enumerate(raw_queries):
        if not isinstance(item, dict):
            continue
        answer = _optional_str(_first(item, "answer", "summary", "reference_answer"))
        question = _optional_str(_first(item, "query", "question"))
        if not question:
            continue
        relevant = _relevant_turn_ids(item, turns)
        queries.append(
            MeetingQuery(
                query_id=f"query-{index + 1:03d}",
                question=question,
                reference_answer=answer,
                query_type=str(item.get("query_type") or query_type),
                relevant_turn_ids=relevant,
                insufficient_evidence=answer is None,
            )
        )
    if not any(query.insufficient_evidence for query in queries):
        queries.append(
            MeetingQuery(
                query_id=f"query-{len(queries) + 1:03d}",
                question="What did the meeting decide about an unrelated launch date?",
                reference_answer=None,
                query_type="negative",
                relevant_turn_ids=[],
                insufficient_evidence=True,
            )
        )
    return queries


def _relevant_turn_ids(item: dict[str, Any], turns: list[TranscriptTurn]) -> list[str]:
    spans = item.get("relevant_text_span") or item.get("relevant_turn_ids") or []
    if isinstance(spans, list) and spans and all(isinstance(value, str) and value.startswith("turn-") for value in spans):
        return [value for value in spans if value in {turn.turn_id for turn in turns}]
    selected: list[str] = []
    if isinstance(spans, list):
        for span in spans:
            if isinstance(span, list) and len(span) >= 2:
                start, end = int(span[0]), int(span[1])
                selected.extend(turn.turn_id for turn in turns[start : end + 1])
            elif isinstance(span, dict):
                start, end = int(span.get("start", 0)), int(span.get("end", 0))
                selected.extend(turn.turn_id for turn in turns[start : end + 1])
    return list(dict.fromkeys(selected))


def _domain(record: dict[str, Any], source_id: str) -> str:
    value = str(_first(record, "domain", "meeting_type", "_source_domain", default="")).lower()
    joined = f"{value} {source_id.lower()}"
    if "product" in joined:
        return "Product"
    if "academic" in joined or "ami" in joined:
        return "Academic"
    return "Committee"


def _iter_records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("data", "meetings", "items", "records"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [data]
    return []


def _domain_from_path(path: Path) -> str:
    lowered = str(path).lower()
    if "product" in lowered:
        return "Product"
    if "academic" in lowered:
        return "Academic"
    if "committee" in lowered:
        return "Committee"
    return "Committee"


def _split_from_path(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    if "val" in parts or "dev" in parts:
        return "validation"
    if "test" in parts:
        return "test"
    if "train" in parts:
        return "train"
    if "all" in parts:
        return "all"
    return "unknown"


def _score_fixture(fixture: MeetingFixture) -> tuple[int, int, int, int]:
    has_specific_span = int(any(query.relevant_turn_ids and query.query_type == "specific" for query in fixture.queries))
    multi_span = int(any(len(query.relevant_turn_ids) >= 2 for query in fixture.queries))
    general = int(any(query.query_type == "general" for query in fixture.queries))
    query_count = len(fixture.queries)
    return has_specific_span, multi_span, general, query_count


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
