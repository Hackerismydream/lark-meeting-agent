# Design: Bootstrap Lark Meeting Agent

## 1. Design Summary

Lark Meeting Agent will be implemented as a deterministic workflow system with typed tool boundaries and schema-validated intelligence outputs.

The MVP should not depend on real Lark credentials or real LLM calls. It should support fake providers and fixture-based tests so that the core workflow can be verified in CI.

## 2. System Architecture

```text
Client / Lark Bot / API
  -> FastAPI API Layer
  -> Workflow Layer
      -> PostMeetingWorkflow
      -> later: PreBriefWorkflow
      -> later: CrossMeetingQAWorkflow
  -> Meeting Intelligence Layer
      -> TranscriptNormalizer
      -> MeetingAnalyzer
      -> EvidenceValidator
      -> WritePlanBuilder
  -> Tool Layer
      -> LarkToolAdapter
      -> FakeLarkProvider
      -> CliLarkProvider
      -> SubprocessRunner
  -> Storage Layer
      -> MeetingRepository
      -> TranscriptRepository
      -> KnowledgeRepository
      -> later: Postgres/pgvector
```

## 3. Key Design Decisions

### Decision 1: Deterministic workflow instead of generic agent loop

The MVP should not use a free-form autonomous agent loop.

Reason:

- Meeting processing has a clear lifecycle.
- Safety requirements are strict.
- Lark write operations must be controlled.
- Deterministic nodes make testing easier.

PostMeetingWorkflow nodes:

```text
ResolveMeeting
FetchTranscript
NormalizeTranscript
AnalyzeMeeting
BuildWritePlan
RequestApproval
ExecuteApprovedWrites
PersistKnowledge
ReturnResult
```

### Decision 2: LarkToolAdapter as the only external Lark boundary

All Lark operations must go through LarkToolAdapter.

Reason:

- Prevent arbitrary shell execution.
- Enforce operation allowlist.
- Separate read and write operations.
- Support fake provider in tests.
- Record audit logs.
- Enforce dry-run and approval.

### Decision 3: Evidence-first meeting intelligence

The analyzer must preserve evidence references for decisions and action items.

Reason:

- Prevent hallucinated commitments.
- Make outputs auditable.
- Support cross-meeting QA with sources.
- Improve user trust.

### Decision 4: Fake provider first

The initial implementation should run without Lark credentials.

Reason:

- CI must be stable.
- Recruiting demo must be reproducible.
- Real Lark permissions may vary.
- Tool behavior should be testable with fixtures.

### Decision 5: Write plan before write execution

The workflow should generate WritePlan first. Execution only happens after approval.

Reason:

- Lark docs, tasks, and IM messages are side-effecting operations.
- Users must preview and approve side effects.
- The same plan can be tested without executing writes.

## 4. Data Model Sketch

### Meeting

Fields:

- id
- title
- start_time
- end_time
- organizer
- attendees
- source
- external_ids

### TranscriptSegment

Fields:

- segment_id
- meeting_id
- speaker_name
- speaker_id
- start_time
- end_time
- text

### EvidenceRef

Fields:

- evidence_id
- meeting_id
- segment_id
- speaker_name
- timestamp
- quote

### MeetingMinutes

Fields:

- meeting_id
- title
- one_sentence_summary
- detailed_summary
- chapters
- decisions
- action_items
- risks
- open_questions

### Decision

Fields:

- decision_id
- text
- owner
- rationale
- evidence_refs

### ActionItem

Fields:

- action_id
- task
- owner
- due_date
- priority
- status
- evidence_refs

### WritePlan

Fields:

- run_id
- operations
- status

### WriteOperation

Fields:

- operation_id
- operation_type
- target
- dry_run_payload
- preview
- requires_approval
- approval_status
- execution_status

## 5. Provider Modes

### Fake Provider

Used in tests and local demos.

Reads fixture files from:

```text
tests/fixtures/lark_cli_outputs/
tests/fixtures/transcripts/
```

### CLI Provider

Later implementation.

Executes allowlisted lark-cli commands through SubprocessRunner.

Rules:

- never expose raw shell to workflows,
- require structured JSON output,
- set timeout,
- redact secrets,
- record audit event.

## 6. API Design

MVP endpoints:

```text
GET /health
POST /api/meetings/process
POST /api/runs/{run_id}/approve
GET /api/runs/{run_id}
POST /api/qa
```

The process endpoint should return:

- run_id,
- status,
- minutes,
- write_plan,
- errors.

## 7. Error Model

Core errors:

- MeetingNotFoundError
- TranscriptNotFoundError
- TranscriptNormalizationError
- AnalyzerValidationError
- MissingEvidenceError
- ApprovalRequiredError
- ToolOperationNotAllowedError
- ToolExecutionError
- PersistenceError

Errors must be explicit and testable.

## 8. Testing Strategy

### Unit tests

- schema validation
- transcript normalization
- evidence validation
- write plan rendering
- safety checks
- tool allowlist

### Integration tests

- fake provider meeting processing
- dry-run write plan
- approval flow
- rejected writes
- cross-meeting QA with sources

### Evaluation fixtures

- transcript samples
- expected decisions
- expected action items
- expected evidence references

## 9. Future Extensions

Later changes may add:

1. pre-brief workflow,
2. real lark-cli provider,
3. database migrations,
4. vector retrieval,
5. realtime meeting event ingestion,
6. Lark bot interaction,
7. web dashboard.
