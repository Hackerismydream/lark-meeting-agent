"""Workspace-local structured meeting memory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nanobot.meeting.errors import PersistenceError
from nanobot.meeting.schemas import (
    EntityMemory,
    LiveMeetingState,
    QAAnswer,
    QASource,
    RetrievalKind,
    Run,
    RunTrace,
)


class MeetingMemoryStore:
    def __init__(self, workspace: Path | str) -> None:
        self.workspace = Path(workspace)
        self.root = self.workspace / ".lark_meeting_agent"
        self.root.mkdir(parents=True, exist_ok=True)

    def persist_run(self, run: Run) -> list[str]:
        try:
            paths = [
                self._append("runs.jsonl", run.model_dump(mode="json")),
            ]
            if run.meeting:
                paths.append(self._append("meetings.jsonl", run.meeting.model_dump(mode="json")))
            for segment in run.transcript_segments:
                paths.append(self._append("transcript_segments.jsonl", segment.model_dump(mode="json")))
            if run.minutes:
                paths.append(self._append("minutes.jsonl", run.minutes.model_dump(mode="json")))
                for decision in run.minutes.decisions:
                    paths.append(self._append("decisions.jsonl", decision.model_dump(mode="json")))
                for action in run.minutes.action_items:
                    paths.append(self._append("action_items.jsonl", action.model_dump(mode="json")))
                for risk in run.minutes.risks:
                    paths.append(self._append("risks.jsonl", risk.model_dump(mode="json")))
                for question in run.minutes.open_questions:
                    paths.append(self._append("open_questions.jsonl", question.model_dump(mode="json")))
            return sorted(set(paths))
        except OSError as exc:
            raise PersistenceError(str(exc)) from exc

    def save_run_snapshot(self, run: Run) -> Path:
        path = self.root / "run_snapshots" / f"{run.run_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(run.model_dump_json(indent=2))
        return path

    def load_run_snapshot(self, run_id: str) -> Run:
        path = self.root / "run_snapshots" / f"{run_id}.json"
        if not path.exists():
            raise PersistenceError(f"run not found: {run_id}")
        return Run.model_validate_json(path.read_text())

    def persist_audit(self, events: list[Any]) -> None:
        for event in events:
            data = event.model_dump(mode="json") if hasattr(event, "model_dump") else event
            self._append("audit.jsonl", data)

    def persist_entity_memory(self, memory: EntityMemory) -> str:
        return self._append("entity_memories.jsonl", memory.model_dump(mode="json"))

    def persist_memory_card(self, card: Any) -> str:
        data = card.model_dump(mode="json") if hasattr(card, "model_dump") else card
        return self._append("memory_cards.jsonl", data)

    def persist_run_trace(self, trace: RunTrace) -> str:
        return self._append("run_traces.jsonl", trace.model_dump(mode="json"))

    def save_live_state(self, state: LiveMeetingState) -> Path:
        path = self.root / "live_states" / f"{state.live_run_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(state.model_dump_json(indent=2))
        return path

    def load_live_state(self, live_run_id: str) -> LiveMeetingState:
        path = self.root / "live_states" / f"{live_run_id}.json"
        if not path.exists():
            raise PersistenceError(f"live run not found: {live_run_id}")
        return LiveMeetingState.model_validate_json(path.read_text())

    def read_records(self, kind: RetrievalKind | str) -> list[dict[str, Any]]:
        filenames = {
            RetrievalKind.TRANSCRIPT_SEGMENT: "transcript_segments.jsonl",
            RetrievalKind.DECISION: "decisions.jsonl",
            RetrievalKind.ACTION_ITEM: "action_items.jsonl",
            RetrievalKind.RISK: "risks.jsonl",
            RetrievalKind.OPEN_QUESTION: "open_questions.jsonl",
            RetrievalKind.MEMORY_CARD: "memory_cards.jsonl",
            RetrievalKind.ENTITY_MEMORY: "entity_memories.jsonl",
            RetrievalKind.MINUTES: "minutes.jsonl",
        }
        key = RetrievalKind(kind) if isinstance(kind, str) else kind
        return self._read_jsonl(filenames[key])

    def open_action_items(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        rows = [row for row in self._read_jsonl("action_items.jsonl") if row.get("status", "open") == "open"]
        if person := filters.get("person"):
            rows = [row for row in rows if person.lower() in json.dumps(row, ensure_ascii=False).lower()]
        if project := filters.get("project"):
            rows = [row for row in rows if project.lower() in json.dumps(row, ensure_ascii=False).lower()]
        if customer := filters.get("customer"):
            rows = [row for row in rows if customer.lower() in json.dumps(row, ensure_ascii=False).lower()]
        return rows

    def qa(self, question: str) -> QAAnswer:
        records = self._read_jsonl("decisions.jsonl") + self._read_jsonl("action_items.jsonl")
        terms = _terms(question)
        matches: list[dict[str, Any]] = []
        for record in records:
            haystack = json.dumps(record, ensure_ascii=False).lower()
            if any(term in haystack for term in terms):
                matches.append(record)
        if not matches:
            return QAAnswer(
                question=question,
                answer="insufficient evidence: 本地会议知识中没有找到足够证据回答该问题。",
                sources=[],
                sufficient=False,
            )
        sources: list[QASource] = []
        snippets: list[str] = []
        for record in matches[:6]:
            text = record.get("text") or record.get("task") or ""
            snippets.append(str(text))
            for evidence in record.get("evidence_refs", [])[:2]:
                sources.append(
                    QASource(
                        meeting_id=evidence.get("meeting_id", ""),
                        segment_id=evidence.get("segment_id"),
                        kind="evidence",
                        text=evidence.get("quote", text),
                        speaker_name=evidence.get("speaker_name"),
                        timestamp=evidence.get("timestamp"),
                    )
                )
        return QAAnswer(
            question=question,
            answer="；".join(snippets),
            sources=sources,
            sufficient=bool(sources),
        )

    def _append(self, filename: str, data: dict[str, Any]) -> str:
        path = self.root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, ensure_ascii=False) + "\n")
        return str(path)

    def _read_jsonl(self, filename: str) -> list[dict[str, Any]]:
        path = self.root / filename
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in path.read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows


def _terms(question: str) -> list[str]:
    base = [part.strip().lower() for part in question.replace("？", " ").replace("?", " ").split() if part.strip()]
    semantic = []
    if "决定" in question:
        semantic.extend(["决定", "灰度", "上线"])
    if "待办" in question:
        semantic.extend(["补充", "确认", "待办"])
    return list(dict.fromkeys([*base, *semantic]))
