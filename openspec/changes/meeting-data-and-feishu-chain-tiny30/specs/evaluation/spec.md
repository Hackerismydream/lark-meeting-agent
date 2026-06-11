# Delta for Meeting Data Evaluation

## ADDED Requirements

### Requirement: Tiny30 Evaluation Suite

The system MUST provide a tiny30 evaluation suite over MeetingBank, QMSum, and VCSum fixtures.

#### Scenario: Evaluation outputs

- GIVEN generated or toy fixtures
- WHEN the tiny30 evaluation runner executes
- THEN it writes `report.json`, `trace.jsonl`, `predictions.jsonl`, and `failures.jsonl`
- AND metrics include schema validity, workflow completion, evidence coverage, trace completeness, artifact consistency, streaming stability, and dataset-specific metrics.

### Requirement: No LLM Judge Gate

The system MUST NOT rely on an LLM judge as the only source of truth.

#### Scenario: Deterministic metric computation

- GIVEN an evaluation run
- WHEN metrics are computed
- THEN deterministic schema, citation, span, trace, and artifact checks are available without a real LLM.
