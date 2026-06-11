# Delta for Data Governance

## ADDED Requirements

### Requirement: Truthful Metric Boundaries

The system MUST separate public corpus metrics, synthetic/mock workflow metrics, real Feishu demo evidence, and real Lark live smoke status.

#### Scenario: Reporting metric claims

- GIVEN a delivery report or evaluation report
- WHEN it describes results
- THEN it marks public dataset metrics as corpus/dev metrics
- AND it does not claim they are production Feishu metrics.

### Requirement: Real Feishu Demo Safety

Real Feishu demo writes MUST be opt-in and sandbox-only.

#### Scenario: Default demo mode

- GIVEN a real Feishu demo script is run without `LMA_DEMO_ENABLE_REAL_WRITES=1`
- WHEN it reaches a write step
- THEN it stays in dry-run mode
- AND it writes local evidence reports only.
