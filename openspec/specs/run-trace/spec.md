# run-trace Specification

## Purpose
TBD - created by archiving change deliver-lifecycle-meeting-agent. Update Purpose after archive.
## Requirements
### Requirement: Workflow Run Trace
Every lifecycle workflow run MUST persist a run trace that records inputs, workflow stage transitions, tool calls, analyzer calls, retrieval calls, write plan operations, approvals, results, and errors.

#### Scenario: Persist pre-brief trace
- **WHEN** `PreBriefWorkflow` completes
- **THEN** the run trace contains the meeting reference, retrieval steps, adapter reads, output summary, and any warnings.

### Requirement: Trace Redaction
Run traces MUST redact secrets, tokens, credentials, private URLs where configured, and raw authorization headers.

#### Scenario: Redact token in trace
- **WHEN** a tool payload or error contains a token-like value
- **THEN** the persisted trace stores a redacted value.

### Requirement: Trace Replay Evidence
Run traces MUST include enough non-secret metadata to reproduce fixture evaluations and debug workflow failures.

#### Scenario: Debug failed benchmark case
- **WHEN** an evaluation case fails
- **THEN** the trace identifies the fixture, workflow stage, failing assertion, and source objects involved.

