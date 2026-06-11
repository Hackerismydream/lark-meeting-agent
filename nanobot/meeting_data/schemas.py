"""Canonical schemas for public meeting data fixtures."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DatasetName(StrEnum):
    MEETINGBANK = "meetingbank"
    QMSUM = "qmsum"
    VCSUM = "vcsum"


class MeetingDataModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=False)


class Provenance(MeetingDataModel):
    source_id: str
    source_path: str | None = None
    source_split: str | None = None
    source_domain: str | None = None
    license: str | None = None
    url: str | None = None
    raw_available: bool = False
    notes: str | None = None


class MeetingMeta(MeetingDataModel):
    title: str
    language: str = "en"
    date: str | None = None
    domain: str | None = None
    city: str | None = None
    agency: str | None = None
    meeting_type: str | None = None
    duration_sec: int | None = None
    source_url: str | None = None


class AgendaItem(MeetingDataModel):
    agenda_id: str
    title: str
    summary: str | None = None
    item_type: str | None = None
    start_turn_id: str | None = None
    end_turn_id: str | None = None
    start_time: str | None = None
    end_time: str | None = None


class TranscriptTurn(MeetingDataModel):
    turn_id: str
    text: str
    speaker: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    start_sec: float | None = None
    end_sec: float | None = None
    agenda_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("transcript turn text must not be empty")
        return value


class TranscriptChunk(MeetingDataModel):
    chunk_id: str
    turn_ids: list[str]
    text: str
    start_sec: float
    end_sec: float

    @field_validator("turn_ids")
    @classmethod
    def turn_ids_must_not_be_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("chunk must include at least one turn id")
        return value


class TopicSegment(MeetingDataModel):
    segment_id: str
    headline: str
    start_turn_id: str
    end_turn_id: str
    summary: str | None = None
    agenda_id: str | None = None
    salient_turn_ids: list[str] = Field(default_factory=list)


class MeetingQuery(MeetingDataModel):
    query_id: str
    question: str
    reference_answer: str | None = None
    query_type: str = "specific"
    relevant_turn_ids: list[str] = Field(default_factory=list)
    insufficient_evidence: bool = False

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query question must not be empty")
        return value


class ActionItemExpectation(MeetingDataModel):
    action_id: str
    task: str
    owner: str | None = None
    due_date: str | None = None
    priority: str | None = None
    evidence_turn_ids: list[str] = Field(default_factory=list)


class DecisionExpectation(MeetingDataModel):
    decision_id: str
    text: str
    owner: str | None = None
    evidence_turn_ids: list[str] = Field(default_factory=list)


class ExpectedArtifacts(MeetingDataModel):
    overall_summary: str | None = None
    segment_summaries: dict[str, str] = Field(default_factory=dict)
    salient_turn_ids: list[str] = Field(default_factory=list)
    action_items: list[ActionItemExpectation] = Field(default_factory=list)
    decisions: list[DecisionExpectation] = Field(default_factory=list)


class MockParticipant(MeetingDataModel):
    participant_id: str
    name: str
    role: str | None = None
    open_id: str | None = None


class MockCalendarEvent(MeetingDataModel):
    event_id: str
    title: str
    start_time: str | None = None
    end_time: str | None = None
    organizer: str | None = None
    participant_ids: list[str] = Field(default_factory=list)


class MockAgendaDoc(MeetingDataModel):
    doc_id: str
    title: str
    markdown: str
    source_agenda_ids: list[str] = Field(default_factory=list)


class MockOutputTargets(MeetingDataModel):
    docs_folder_token: str | None = None
    task_list_guid: str | None = None
    chat_id: str | None = None
    decision_doc_token: str | None = None
    sandbox_only: bool = True


class FeishuLikeMeetingContext(MeetingDataModel):
    fixture_id: str
    calendar_event: MockCalendarEvent
    agenda_doc: MockAgendaDoc | None = None
    participants: list[MockParticipant] = Field(default_factory=list)
    transcript_stream: list[TranscriptChunk] = Field(default_factory=list)
    meeting_chat_events: list[dict[str, Any]] = Field(default_factory=list)
    related_docs: list[dict[str, Any]] = Field(default_factory=list)
    output_targets: MockOutputTargets = Field(default_factory=MockOutputTargets)
    approval_policy: Literal["dry_run_required", "sandbox_writes_only"] = "dry_run_required"


class MeetingFixture(MeetingDataModel):
    fixture_id: str
    dataset: DatasetName
    meta: MeetingMeta
    provenance: Provenance
    agenda: list[AgendaItem] = Field(default_factory=list)
    transcript_turns: list[TranscriptTurn]
    transcript_chunks: list[TranscriptChunk] = Field(default_factory=list)
    topic_segments: list[TopicSegment] = Field(default_factory=list)
    queries: list[MeetingQuery] = Field(default_factory=list)
    expected: ExpectedArtifacts = Field(default_factory=ExpectedArtifacts)

    @field_validator("fixture_id")
    @classmethod
    def fixture_id_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("fixture_id is required")
        return value

    @field_validator("transcript_turns")
    @classmethod
    def transcript_turns_must_not_be_empty(cls, value: list[TranscriptTurn]) -> list[TranscriptTurn]:
        if not value:
            raise ValueError("transcript_turns must be non-empty")
        return value

    @model_validator(mode="after")
    def validate_references(self) -> "MeetingFixture":
        turn_ids = [turn.turn_id for turn in self.transcript_turns]
        _ensure_unique(turn_ids, "turn_id")
        agenda_ids = [item.agenda_id for item in self.agenda]
        _ensure_unique(agenda_ids, "agenda_id")
        query_ids = [query.query_id for query in self.queries]
        _ensure_unique(query_ids, "query_id")

        turn_id_set = set(turn_ids)
        agenda_id_set = set(agenda_ids)
        for query in self.queries:
            missing = sorted(set(query.relevant_turn_ids) - turn_id_set)
            if missing:
                raise ValueError(f"query {query.query_id} references missing turn ids: {missing}")
        for segment in self.topic_segments:
            for key, turn_id in [("start_turn_id", segment.start_turn_id), ("end_turn_id", segment.end_turn_id)]:
                if turn_id not in turn_id_set:
                    raise ValueError(f"segment {segment.segment_id} {key} references missing turn id: {turn_id}")
            missing_salient = sorted(set(segment.salient_turn_ids) - turn_id_set)
            if missing_salient:
                raise ValueError(f"segment {segment.segment_id} references missing salient turns: {missing_salient}")
            if segment.agenda_id and agenda_id_set and segment.agenda_id not in agenda_id_set:
                raise ValueError(f"segment {segment.segment_id} references missing agenda id: {segment.agenda_id}")
        for artifact_id in self.expected.salient_turn_ids:
            if artifact_id not in turn_id_set:
                raise ValueError(f"expected salient turn references missing turn id: {artifact_id}")
        for action in self.expected.action_items:
            missing = sorted(set(action.evidence_turn_ids) - turn_id_set)
            if missing:
                raise ValueError(f"action {action.action_id} references missing turn ids: {missing}")
        for decision in self.expected.decisions:
            missing = sorted(set(decision.evidence_turn_ids) - turn_id_set)
            if missing:
                raise ValueError(f"decision {decision.decision_id} references missing turn ids: {missing}")
        return self


def _ensure_unique(values: list[str], label: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        raise ValueError(f"{label} must be unique inside fixture: {sorted(duplicates)}")
