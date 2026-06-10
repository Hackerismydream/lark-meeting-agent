# Design: Bootstrap Lark Meeting Agent

## 1. Design Summary

Lark Meeting Agent will be implemented as a deterministic meeting-domain extension inside a HKUDS/nanobot v0.2.1 fork/source checkout.

The MVP should not depend on real Lark credentials or real LLM calls. It should support fake providers, fake analyzers, and fixture-based tests so the core meeting workflow can be verified in CI without Feishu, nanobot gateway, or external model access.

This change is documentation and OpenSpec only. It does not create application code.

## 2. System Architecture

```text
Feishu / WebUI / CLI / other nanobot channels
  -> nanobot MessageBus / AgentLoop / CommandRouter
  -> Lark Meeting entrypoint
      -> deterministic PostMeetingWorkflow
          -> ResolveMeeting
          -> FetchTranscript
          -> NormalizeTranscript
          -> AnalyzeMeeting
          -> BuildWritePlan
          -> RequestApproval
          -> ExecuteApprovedWrites
          -> PersistKnowledge
          -> ReturnResult
      -> Meeting Intelligence
      -> LarkToolAdapter
      -> Meeting Memory
  -> nanobot session/memory/provider/WebUI/deployment infrastructure
```

## 3. Future Code Shape

Do not create these files in this change. This is the intended later shape:

```text
nanobot/meeting/
  schemas.py
  workflow.py
  analyzer.py
  normalizer.py
  lark_adapter.py
  write_plan.py
  memory.py
  renderers.py
  evals.py

nanobot/agent/tools/lark_meeting.py
  # Thin tool wrapper around deterministic meeting workflows.

nanobot/skills/lark-meeting/SKILL.md
  # Agent-facing instructions for when and how to use meeting tools.

tests/meeting/
tests/fixtures/meeting/
```

## 4. Key Design Decisions

### Decision 1: Adopt nanobot v0.2.1 instead of standalone FastAPI

The MVP should not start from a new FastAPI app.

Reason:

- nanobot already provides the agent runtime, Feishu channel, tools, memory, WebUI, model routing, MCP, deployment, and security/workspace controls.
- The meeting product value is in domain workflows, evidence, approval, and Lark-safe tool boundaries.
- Rebuilding the base runtime would expand scope before the meeting vertical slice works.

### Decision 2: Deterministic workflow instead of a second generic agent loop

nanobot AgentLoop may route user messages into the meeting entrypoint, but PostMeetingWorkflow remains deterministic.

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

Reason:

- Meeting processing has a clear lifecycle.
- Safety requirements are strict.
- Lark write operations must be controlled.
- Deterministic nodes make testing easier.

### Decision 3: LarkToolAdapter as the only external Lark boundary

All Lark operations must go through LarkToolAdapter.

Reason:

- Prevent arbitrary shell execution.
- Prevent nanobot's general exec tool from bypassing approval.
- Enforce operation allowlist.
- Separate read and write operations.
- Support fake provider in tests.
- Record audit logs.
- Enforce dry-run and approval.

### Decision 4: Evidence-first meeting intelligence

The analyzer must preserve evidence references for decisions and action items.

Reason:

- Prevent hallucinated commitments.
- Make outputs auditable.
- Support cross-meeting QA with sources.
- Improve user trust.

### Decision 5: Fake provider and fake analyzer first

The initial implementation should run without Lark credentials and without real LLM API keys.

Reason:

- CI must be stable.
- Recruiting demo must be reproducible.
- Real Lark permissions may vary.
- Tool behavior should be testable with fixtures.
- Analyzer contracts should be testable before model selection.

### Decision 6: Write plan before write execution

The workflow should generate WritePlan first. Execution only happens after approval.

Reason:

- Lark docs, tasks, and IM messages are side-effecting operations.
- Users must preview and approve side effects.
- The same plan can be tested without executing writes.

## 5. nanobot Extension-point Research Required Before Implementation

Before implementing runtime code, Codex must inspect nanobot v0.2.1 extension points:

- AgentLoop
- CommandRouter
- Tool and ToolLoader
- Feishu channel
- skills
- memory
- security/workspace settings
- Python SDK
- OpenAI-compatible API
- WebUI/gateway

The implementation plan must be updated if the researched extension points indicate a better integration surface.

## 6. Entrypoint Design

Preferred conceptual entrypoints:

```text
/meeting process
/meeting approve
/meeting qa
```

Equivalent tool action contract is acceptable if command registration is not selected after research:

```text
lark_meeting(action="process")
lark_meeting(action="approve")
lark_meeting(action="qa")
```

Standalone REST/OpenAI-compatible API integration is future scope, not the MVP primary entrypoint.

## 7. Data Model Sketch

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

## 8. Provider Modes

### Fake Provider

Used in tests and local demos.

Future fixture roots:

```text
tests/fixtures/meeting/transcripts/
tests/fixtures/meeting/lark_outputs/
tests/fixtures/meeting/expected/
```

### CLI Provider

Later implementation only.

If a CLI provider uses `lark-cli`, it executes allowlisted commands only through LarkToolAdapter.

Rules:

- never expose raw shell to workflows,
- never invoke `lark-cli` through nanobot's general exec tool,
- require structured JSON output,
- set timeout,
- redact secrets,
- record audit event,
- require dry-run and approval for writes.

## 9. Safety Settings

Production-like meeting-agent configs should:

- set `tools.exec.enable=false` unless shell execution is explicitly needed for development,
- set `tools.restrictToWorkspace=true`,
- use sandbox settings where available,
- restrict Feishu users through `allowFrom`,
- restrict group behavior through group policy.

If exec is enabled, Lark-related shell commands must still be blocked by policy and cannot bypass LarkToolAdapter.

## 10. Error Model

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
- UnauthorizedMeetingWorkflowError

Errors must be explicit and testable.

## 11. Testing Strategy

### Unit tests

- schema validation
- transcript normalization
- evidence validation
- write plan rendering
- safety checks
- tool allowlist
- command/tool entrypoint validation

### Integration tests

- fake provider meeting processing
- fake analyzer mode
- dry-run write plan
- approval flow
- rejected writes
- selected approved writes
- cross-meeting QA with sources

### Evaluation fixtures

- transcript samples
- expected decisions
- expected action items
- expected evidence references

CI tests must not require:

- real Lark credentials,
- real LLM API keys,
- Feishu channel connectivity,
- nanobot gateway.

## 12. Future Extensions

Later changes may add:

1. pre-brief workflow,
2. real lark-cli provider,
3. storage backend changes if needed after nanobot research,
4. vector retrieval,
5. realtime meeting event ingestion,
6. richer Lark bot interaction.
