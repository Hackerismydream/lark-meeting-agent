"""Local retrieval over workspace meeting memory."""

from __future__ import annotations

import json
from typing import Any

from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.schemas import (
    QASource,
    RetrievalKind,
    RetrievalQuery,
    RetrievalResult,
    RetrievalResultItem,
)


class MeetingRetrievalEngine:
    def __init__(self, store: MeetingMemoryStore) -> None:
        self.store = store

    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        terms = _terms(query.question, query.project, query.customer, query.person)
        kinds = query.kinds or list(RetrievalKind)
        candidates: list[RetrievalResultItem] = []
        for kind in kinds:
            for record in self.store.read_records(kind):
                text = _record_text(record)
                if not _passes_filters(record, query):
                    continue
                score = _score(text, record, terms)
                if score <= 0:
                    continue
                candidates.append(
                    RetrievalResultItem(
                        kind=kind,
                        text=text,
                        score=score,
                        source=_source_for(record, kind, text),
                        metadata=_metadata_for(record),
                    )
                )
        candidates.sort(key=lambda item: item.score, reverse=True)
        items = candidates[: query.limit]
        return RetrievalResult(query=query, items=items, sufficient=bool(items))

    def answer(self, question: str, **filters: Any):
        query = RetrievalQuery(question=question, **filters)
        result = self.retrieve(query)
        if not result.items:
            from nanobot.meeting.schemas import QAAnswer

            return QAAnswer(
                question=question,
                answer="insufficient evidence: 本地会议知识中没有找到足够证据回答该问题。",
                sufficient=False,
            )
        from nanobot.meeting.schemas import QAAnswer

        return QAAnswer(
            question=question,
            answer="；".join(item.text for item in result.items[:4]),
            sources=[item.source for item in result.items],
            sufficient=True,
        )


class DeterministicSemanticRetriever:
    """Small local semantic stand-in for tests; production vector search can replace it."""

    def rank(self, query: str, texts: list[str]) -> list[tuple[str, float]]:
        query_chars = set(query.lower())
        ranked = []
        for text in texts:
            overlap = len(query_chars.intersection(set(text.lower())))
            ranked.append((text, float(overlap)))
        return sorted(ranked, key=lambda item: item[1], reverse=True)


def _terms(*values: str | None) -> list[str]:
    terms: list[str] = []
    for value in values:
        if not value:
            continue
        normalized = value.replace("？", " ").replace("?", " ").replace("，", " ")
        terms.extend(part.strip().lower() for part in normalized.split() if part.strip())
    semantic = []
    joined = " ".join(value or "" for value in values)
    if "决定" in joined:
        semantic.extend(["决定", "上线", "采用", "确认"])
    if "待办" in joined or "承诺" in joined:
        semantic.extend(["待办", "负责", "补充", "确认"])
    if "风险" in joined:
        semantic.extend(["风险", "阻塞", "延期"])
    return list(dict.fromkeys([*terms, *semantic]))


def _score(text: str, record: dict[str, Any], terms: list[str]) -> float:
    haystack = f"{text} {json.dumps(record, ensure_ascii=False)}".lower()
    return float(sum(1 for term in terms if term and term in haystack))


def _passes_filters(record: dict[str, Any], query: RetrievalQuery) -> bool:
    blob = json.dumps(record, ensure_ascii=False).lower()
    for value in (query.project, query.customer, query.person):
        if value and value.lower() not in blob:
            return False
    return True


def _record_text(record: dict[str, Any]) -> str:
    for key in ("text", "task", "summary", "content", "one_sentence_summary", "detailed_summary"):
        value = record.get(key)
        if value:
            return str(value)
    return json.dumps(record, ensure_ascii=False)


def _source_for(record: dict[str, Any], kind: RetrievalKind, text: str) -> QASource:
    evidence = (record.get("evidence_refs") or [{}])[0]
    return QASource(
        meeting_id=str(evidence.get("meeting_id") or record.get("meeting_id") or ""),
        segment_id=evidence.get("segment_id") or record.get("segment_id"),
        kind=kind.value,
        text=str(evidence.get("quote") or text),
        speaker_name=evidence.get("speaker_name") or record.get("speaker_name"),
        timestamp=evidence.get("timestamp") or record.get("start_time"),
    )


def _metadata_for(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if key in {"decision_id", "action_id", "risk_id", "question_id", "entity_id", "entity_type", "status", "due_date"}
    }
