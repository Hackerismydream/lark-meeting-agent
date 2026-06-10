"""Pydantic schemas for meeting workflows."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProviderMode(StrEnum):
    FAKE = "fake"
    CLI = "cli"
    OAPI = "oapi"


class AnalyzerMode(StrEnum):
    FAKE = "fake"
    LLM = "llm"


class MeetingRefType(StrEnum):
    LATEST_ENDED = "latest_ended"
    MEETING_ID = "meeting_id"
    MINUTE_TOKEN = "minute_token"
    TRANSCRIPT_FILE = "transcript_file"


class MeetingType(StrEnum):
    CUSTOMER_MEETING = "customer_meeting"
    PROJECT_SYNC = "project_sync"
    REQUIREMENT_REVIEW = "requirement_review"
    TECHNICAL_REVIEW = "technical_review"
    INCIDENT_REVIEW = "incident_review"
    ONE_ON_ONE = "one_on_one"
    GENERAL = "general"


class LiveEventKind(StrEnum):
    TRANSCRIPT_DELTA = "transcript_delta"
    TOPIC_CHANGE = "topic_change"
    PARTICIPANT_JOIN = "participant_join"
    PARTICIPANT_LEAVE = "participant_leave"
    MARKER = "marker"


class MemoryEntityType(StrEnum):
    PROJECT = "project"
    CUSTOMER = "customer"
    PERSON = "person"


class RetrievalKind(StrEnum):
    TRANSCRIPT_SEGMENT = "transcript_segment"
    DECISION = "decision"
    ACTION_ITEM = "action_item"
    RISK = "risk"
    OPEN_QUESTION = "open_question"
    MEMORY_CARD = "memory_card"
    ENTITY_MEMORY = "entity_memory"
    MINUTES = "minutes"


class OperationType(StrEnum):
    DOC_CREATE = "docs.create"
    TASK_CREATE = "task.create"
    IM_SEND = "im.send"


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MISSING_TARGET = "missing_target"


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    DRY_RUN = "dry_run"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    APPROVAL_REQUIRED = "approval_required"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class ReadOrWrite(StrEnum):
    READ = "read"
    WRITE = "write"


class MeetingBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=False)


class Attendee(MeetingBaseModel):
    name: str
    open_id: str | None = None


class Meeting(MeetingBaseModel):
    meeting_id: str
    title: str
    start_time: str | None = None
    end_time: str | None = None
    organizer: str | None = None
    attendees: list[Attendee] = Field(default_factory=list)
    source: str = "fixture"
    external_ids: dict[str, str] = Field(default_factory=dict)


class TranscriptSegment(MeetingBaseModel):
    segment_id: str
    meeting_id: str
    text: str
    speaker_name: str | None = None
    speaker_id: str | None = None
    start_time: str | None = None
    end_time: str | None = None

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("segment text must not be empty")
        return value.strip()


class EvidenceRef(MeetingBaseModel):
    evidence_id: str
    meeting_id: str
    segment_id: str
    speaker_name: str | None = None
    timestamp: str | None = None
    quote: str

    @field_validator("quote")
    @classmethod
    def quote_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("evidence quote must not be empty")
        return value.strip()


class Chapter(MeetingBaseModel):
    title: str
    summary: str
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class Decision(MeetingBaseModel):
    decision_id: str
    text: str
    owner: str | None = None
    rationale: str | None = None
    evidence_refs: list[EvidenceRef]

    @field_validator("evidence_refs")
    @classmethod
    def evidence_required(cls, value: list[EvidenceRef]) -> list[EvidenceRef]:
        if not value:
            raise ValueError("decision requires at least one evidence ref")
        return value


class ActionItem(MeetingBaseModel):
    action_id: str
    task: str
    owner: str | None = None
    due_date: str | None = None
    priority: str | None = None
    status: str = "open"
    evidence_refs: list[EvidenceRef]

    @field_validator("evidence_refs")
    @classmethod
    def evidence_required(cls, value: list[EvidenceRef]) -> list[EvidenceRef]:
        if not value:
            raise ValueError("action item requires at least one evidence ref")
        return value


class Risk(MeetingBaseModel):
    risk_id: str
    text: str
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class OpenQuestion(MeetingBaseModel):
    question_id: str
    text: str
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class MeetingMinutes(MeetingBaseModel):
    meeting_id: str
    title: str
    one_sentence_summary: str
    detailed_summary: str
    chapters: list[Chapter] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)


class WriteOperation(MeetingBaseModel):
    operation_id: str
    operation_type: OperationType
    target: dict[str, Any] = Field(default_factory=dict)
    dry_run_payload: dict[str, Any] = Field(default_factory=dict)
    preview: str
    idempotency_key: str = ""
    requires_approval: bool = True
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    execution_status: ExecutionStatus = ExecutionStatus.PENDING
    result: dict[str, Any] | None = None
    error: str | None = None


class WritePlan(MeetingBaseModel):
    run_id: str
    operations: list[WriteOperation] = Field(default_factory=list)
    status: str = "pending"


class ToolCallAuditEvent(MeetingBaseModel):
    audit_id: str
    operation_name: str
    provider_mode: ProviderMode
    sanitized_input: dict[str, Any] = Field(default_factory=dict)
    read_or_write: ReadOrWrite
    dry_run: bool
    approval_status: ApprovalStatus | None = None
    execution_status: ExecutionStatus
    exit_code: int | None = None
    result_summary: str | None = None
    error_message: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TranscriptGateSource(MeetingBaseModel):
    source_type: str
    meeting_id: str | None = None
    minute_token: str | None = None
    title: str | None = None
    text_preview: str


class TranscriptGateAttempt(MeetingBaseModel):
    meeting_id: str
    title: str | None = None
    reason: str


class TranscriptGateReport(MeetingBaseModel):
    status: str
    provider_mode: ProviderMode
    query: str | None = None
    start: str | None = None
    end: str | None = None
    visible_meeting_count: int = 0
    accessible_minute_count: int = 0
    readable_source: TranscriptGateSource | None = None
    checked_meetings: list[TranscriptGateAttempt] = Field(default_factory=list)
    blocker_message: str | None = None
    next_process_command: str | None = None


class MemoryCard(MeetingBaseModel):
    entity_type: str
    entity_id: str | None = None
    name: str | None = None
    content: str
    confidence: float = 0.5
    source_meeting_ids: list[str] = Field(default_factory=list)
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class QASource(MeetingBaseModel):
    meeting_id: str
    segment_id: str | None = None
    kind: str
    text: str
    speaker_name: str | None = None
    timestamp: str | None = None


class QAAnswer(MeetingBaseModel):
    question: str
    answer: str
    sources: list[QASource] = Field(default_factory=list)
    sufficient: bool = True


class MeetingRef(MeetingBaseModel):
    type: MeetingRefType
    value: str | None = None
    query: str | None = None


class PreBriefInput(MeetingBaseModel):
    meeting_ref: MeetingRef
    provider_mode: ProviderMode = ProviderMode.FAKE
    meeting_type: MeetingType = MeetingType.GENERAL
    project: str | None = None
    customer: str | None = None
    participants: list[str] = Field(default_factory=list)
    time_range: dict[str, str] = Field(default_factory=dict)


class PreBriefSection(MeetingBaseModel):
    title: str
    bullets: list[str] = Field(default_factory=list)
    sources: list[QASource] = Field(default_factory=list)


class PreBrief(MeetingBaseModel):
    run_id: str
    meeting: Meeting | None = None
    meeting_type: MeetingType
    goal: str
    sections: list[PreBriefSection] = Field(default_factory=list)
    suggested_questions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    trace_path: str | None = None


class LiveMeetingEvent(MeetingBaseModel):
    event_id: str
    live_run_id: str
    meeting_id: str
    kind: LiveEventKind
    text: str | None = None
    speaker_name: str | None = None
    timestamp: str | None = None
    segment_id: str | None = None


class CandidateStatus(StrEnum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    INCOMPLETE = "incomplete"


class LiveDecisionCandidate(MeetingBaseModel):
    candidate_id: str
    text: str
    status: CandidateStatus = CandidateStatus.CANDIDATE
    evidence_refs: list[EvidenceRef]

    @field_validator("evidence_refs")
    @classmethod
    def evidence_required(cls, value: list[EvidenceRef]) -> list[EvidenceRef]:
        if not value:
            raise ValueError("live decision candidate requires evidence")
        return value


class LiveActionCandidate(MeetingBaseModel):
    candidate_id: str
    task: str
    owner: str | None = None
    due_date: str | None = None
    status: CandidateStatus = CandidateStatus.CANDIDATE
    evidence_refs: list[EvidenceRef]

    @field_validator("evidence_refs")
    @classmethod
    def evidence_required(cls, value: list[EvidenceRef]) -> list[EvidenceRef]:
        if not value:
            raise ValueError("live action candidate requires evidence")
        return value


class LiveMeetingState(MeetingBaseModel):
    live_run_id: str
    meeting_id: str
    title: str = "live meeting"
    current_topic: str | None = None
    rolling_summary: str = ""
    transcript_segments: list[TranscriptSegment] = Field(default_factory=list)
    decision_candidates: list[LiveDecisionCandidate] = Field(default_factory=list)
    action_candidates: list[LiveActionCandidate] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LiveQAAnswer(QAAnswer):
    live_run_id: str


class EntityMemory(MeetingBaseModel):
    entity_type: MemoryEntityType
    entity_id: str
    name: str
    summary: str
    source_meeting_ids: list[str] = Field(default_factory=list)
    source_segment_ids: list[str] = Field(default_factory=list)
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RetrievalQuery(MeetingBaseModel):
    question: str
    project: str | None = None
    customer: str | None = None
    person: str | None = None
    time_range: dict[str, str] = Field(default_factory=dict)
    kinds: list[RetrievalKind] = Field(default_factory=list)
    limit: int = 8


class RetrievalResultItem(MeetingBaseModel):
    kind: RetrievalKind
    text: str
    score: float
    source: QASource
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalResult(MeetingBaseModel):
    query: RetrievalQuery
    items: list[RetrievalResultItem] = Field(default_factory=list)
    sufficient: bool = False


class RunTraceEvent(MeetingBaseModel):
    event_id: str
    stage: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RunTrace(MeetingBaseModel):
    run_id: str
    workflow: str
    events: list[RunTraceEvent] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EvaluationExpected(MeetingBaseModel):
    decisions: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    qa_answer_terms: list[str] = Field(default_factory=list)
    evidence_segment_ids: list[str] = Field(default_factory=list)


class EvaluationCase(MeetingBaseModel):
    case_id: str
    meeting_type: MeetingType = MeetingType.GENERAL
    transcript: str
    question: str | None = None
    expected: EvaluationExpected = Field(default_factory=EvaluationExpected)


class EvaluationMetrics(MeetingBaseModel):
    action_precision: float = 0.0
    action_recall: float = 0.0
    decision_precision: float = 0.0
    decision_recall: float = 0.0
    evidence_coverage: float = 0.0
    schema_validation_success_rate: float = 0.0
    tool_call_success_rate: float = 0.0
    qa_source_accuracy: float = 0.0
    safety_pass_rate: float = 0.0


class EvaluationReport(MeetingBaseModel):
    profile: str
    metrics: EvaluationMetrics
    passed: bool
    case_results: list[dict[str, Any]] = Field(default_factory=list)
    trace_paths: list[str] = Field(default_factory=list)


class ProcessMeetingInput(MeetingBaseModel):
    meeting_ref: MeetingRef
    provider_mode: ProviderMode = ProviderMode.FAKE
    analyzer_mode: AnalyzerMode = AnalyzerMode.FAKE
    create_doc: bool = True
    create_tasks: bool = True
    send_message: bool = False
    chat_id: str | None = None
    dry_run: bool = True


class ProcessMeetingResult(MeetingBaseModel):
    run_id: str
    status: RunStatus
    meeting: Meeting | None = None
    minutes: MeetingMinutes | None = None
    write_plan: WritePlan | None = None
    persisted_paths: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class ApproveInput(MeetingBaseModel):
    run_id: str
    approved_operation_ids: list[str]


class ApproveResult(MeetingBaseModel):
    run_id: str
    status: RunStatus
    write_plan: WritePlan
    errors: list[str] = Field(default_factory=list)


class QAInput(MeetingBaseModel):
    question: str
    filters: dict[str, Any] = Field(default_factory=dict)


class Run(MeetingBaseModel):
    run_id: str
    status: RunStatus
    provider_mode: ProviderMode = ProviderMode.FAKE
    analyzer_mode: AnalyzerMode = AnalyzerMode.FAKE
    meeting: Meeting | None = None
    transcript_segments: list[TranscriptSegment] = Field(default_factory=list)
    minutes: MeetingMinutes | None = None
    write_plan: WritePlan | None = None
    errors: list[str] = Field(default_factory=list)
    write_plan_created_at: str | None = None
    approved_at: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
