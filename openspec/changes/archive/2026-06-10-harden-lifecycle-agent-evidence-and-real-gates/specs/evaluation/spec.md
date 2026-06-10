## ADDED Requirements

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
