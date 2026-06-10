## ADDED Requirements

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
