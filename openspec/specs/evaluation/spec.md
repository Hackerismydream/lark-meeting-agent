# Evaluation Spec

## Purpose

Define evaluation requirements for meeting-agent extraction, safety, and QA behavior.
## Requirements
### Requirement: CI Validation Gates
The lifecycle implementation MUST pass local tests and lint without real Lark or LLM credentials.

#### Scenario: Meeting test suite
- **WHEN** `pytest tests/meeting -q` runs
- **THEN** lifecycle workflows, adapter, memory, retrieval, evaluation, and safety tests pass.

### Requirement: Optional Real Smoke Gates
The repository MUST provide optional real smoke commands for DeepSeek analysis, lark-cli reads, and approved write execution.

#### Scenario: Real smoke unavailable
- **WHEN** real Lark minutes are unavailable for the current account
- **THEN** the smoke command reports the external blocker without failing CI.

### Requirement: Benchmark Report Artifact
The evaluation command MUST write a machine-readable report with metrics and case-level failures.

#### Scenario: Report generated
- **WHEN** lifecycle evaluation completes
- **THEN** a JSON report exists with aggregate metrics, per-case results, and trace paths.

### Requirement: Deterministic regression benchmark naming
The current 31-case fixture benchmark MUST be named deterministic fixture regression benchmark.

#### Scenario: Report profile
- **WHEN** the bundled lifecycle evaluation runs
- **THEN** the report profile identifies deterministic regression rather than production or LLM metrics.

### Requirement: Optional LLM extraction benchmark contract
The system MUST include an optional LLM extraction benchmark contract that is skipped unless real LLM tests are enabled.

#### Scenario: LLM tests disabled
- **WHEN** `RUN_REAL_LLM_TESTS` is not set
- **THEN** optional LLM benchmark tests are skipped.

#### Scenario: LLM benchmark fixtures
- **WHEN** optional LLM benchmark fixtures are inspected
- **THEN** they include expected decisions, action items, and evidence segment IDs.
