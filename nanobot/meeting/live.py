"""Live meeting workflow over incremental transcript events."""

from __future__ import annotations

import uuid
from pathlib import Path

from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.schemas import (
    EvidenceRef,
    LiveActionCandidate,
    LiveDecisionCandidate,
    LiveEventKind,
    LiveMeetingEvent,
    LiveMeetingState,
    LiveQAAnswer,
    OpenQuestion,
    QASource,
    Risk,
    TranscriptSegment,
)
from nanobot.meeting.trace import RunTraceWriter


class LiveMeetingWorkflow:
    def __init__(self, workspace: Path | str) -> None:
        self.workspace = Path(workspace)
        self.memory = MeetingMemoryStore(self.workspace)

    def start(self, meeting_id: str, title: str = "live meeting") -> LiveMeetingState:
        live_run_id = str(uuid.uuid4())
        state = LiveMeetingState(live_run_id=live_run_id, meeting_id=meeting_id, title=title)
        self.memory.save_live_state(state)
        trace = RunTraceWriter(self.workspace, live_run_id, "LiveMeetingWorkflow")
        trace.add("start", "live meeting started", {"meeting_id": meeting_id, "title": title})
        trace.save()
        return state

    def ingest(self, event: LiveMeetingEvent) -> LiveMeetingState:
        try:
            state = self.memory.load_live_state(event.live_run_id)
        except Exception:
            state = LiveMeetingState(live_run_id=event.live_run_id, meeting_id=event.meeting_id)
        if event.kind == LiveEventKind.TOPIC_CHANGE and event.text:
            state.current_topic = event.text.strip()
        if event.kind == LiveEventKind.TRANSCRIPT_DELTA and event.text:
            segment = TranscriptSegment(
                segment_id=event.segment_id or f"seg-{len(state.transcript_segments) + 1:04d}",
                meeting_id=event.meeting_id,
                text=event.text,
                speaker_name=event.speaker_name,
                start_time=event.timestamp,
            )
            state.transcript_segments.append(segment)
            evidence = EvidenceRef(
                evidence_id=f"ev-{segment.segment_id}",
                meeting_id=segment.meeting_id,
                segment_id=segment.segment_id,
                speaker_name=segment.speaker_name,
                timestamp=segment.start_time,
                quote=segment.text,
            )
            self._update_candidates(state, segment.text, evidence)
            state.rolling_summary = _rolling_summary(state.transcript_segments)
        self.memory.save_live_state(state)
        return state

    def qa(self, live_run_id: str, question: str) -> LiveQAAnswer:
        state = self.memory.load_live_state(live_run_id)
        terms = _terms(question)
        sources: list[QASource] = []
        snippets: list[str] = []
        candidate_rows = [
            *(candidate.model_dump(mode="json") for candidate in state.decision_candidates),
            *(candidate.model_dump(mode="json") for candidate in state.action_candidates),
            *(risk.model_dump(mode="json") for risk in state.risks),
            *(question_obj.model_dump(mode="json") for question_obj in state.open_questions),
        ]
        for row in candidate_rows:
            text = str(row.get("text") or row.get("task") or "")
            if not terms or any(term in text.lower() for term in terms):
                snippets.append(text)
                for evidence in row.get("evidence_refs", [])[:2]:
                    sources.append(
                        QASource(
                            meeting_id=evidence.get("meeting_id", state.meeting_id),
                            segment_id=evidence.get("segment_id"),
                            kind="live_evidence",
                            text=evidence.get("quote", text),
                            speaker_name=evidence.get("speaker_name"),
                            timestamp=evidence.get("timestamp"),
                        )
                    )
        if not sources and ("刚才" in question or "讨论" in question):
            for segment in state.transcript_segments[-3:]:
                snippets.append(segment.text)
                sources.append(
                    QASource(
                        meeting_id=segment.meeting_id,
                        segment_id=segment.segment_id,
                        kind="transcript_segment",
                        text=segment.text,
                        speaker_name=segment.speaker_name,
                        timestamp=segment.start_time,
                    )
                )
        if not sources:
            return LiveQAAnswer(
                live_run_id=live_run_id,
                question=question,
                answer="insufficient evidence: 当前会议状态中没有足够证据回答该问题。",
                sources=[],
                sufficient=False,
            )
        return LiveQAAnswer(
            live_run_id=live_run_id,
            question=question,
            answer="；".join(dict.fromkeys(snippets[:6])),
            sources=sources,
            sufficient=True,
        )

    def _update_candidates(self, state: LiveMeetingState, text: str, evidence: EvidenceRef) -> None:
        normalized = text.lower()
        if "决定" in text or "确认" in text or "采用" in text:
            state.decision_candidates.append(
                LiveDecisionCandidate(
                    candidate_id=f"ld-{len(state.decision_candidates) + 1:03d}",
                    text=text,
                    evidence_refs=[evidence],
                )
            )
        if "负责" in text or "待办" in text or "补充" in text or "跟进" in text:
            state.action_candidates.append(
                LiveActionCandidate(
                    candidate_id=f"la-{len(state.action_candidates) + 1:03d}",
                    task=text,
                    owner=_owner_from_text(text),
                    evidence_refs=[evidence],
                )
            )
        if "风险" in text or "阻塞" in text or "延期" in text or "risk" in normalized:
            state.risks.append(
                Risk(
                    risk_id=f"lr-{len(state.risks) + 1:03d}",
                    text=text,
                    evidence_refs=[evidence],
                )
            )
        if "？" in text or "?" in text or "问题" in text:
            state.open_questions.append(
                OpenQuestion(
                    question_id=f"lq-{len(state.open_questions) + 1:03d}",
                    text=text,
                    evidence_refs=[evidence],
                )
            )


def _rolling_summary(segments: list[TranscriptSegment]) -> str:
    recent = segments[-5:]
    return " ".join(segment.text for segment in recent)


def _terms(question: str) -> list[str]:
    terms = [part.strip().lower() for part in question.replace("？", " ").replace("?", " ").split() if part.strip()]
    if "结论" in question or "决定" in question:
        terms.extend(["决定", "确认", "采用"])
    if "承诺" in question or "待办" in question:
        terms.extend(["负责", "待办", "补充", "跟进"])
    return list(dict.fromkeys(terms))


def _owner_from_text(text: str) -> str | None:
    for marker in ("负责", "来"):
        if marker in text:
            prefix = text.split(marker, 1)[0].strip(" ，,。")
            name = prefix.split()[-1] if prefix.split() else prefix[-8:]
            return name or None
    return None
