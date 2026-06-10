# Delta for Evaluation

## ADDED Requirements

### Requirement: Fixture-based Evaluation

The repository MUST include fixture-based evaluation assets for meeting intelligence.

Fixtures SHOULD include transcript samples, expected decisions, expected action items, expected owners, expected due dates, and expected evidence segment IDs.

Evaluations MUST run with pytest and pytest-asyncio where async behavior is involved.

#### Scenario: Golden transcript test

- GIVEN a transcript fixture with known action items
- WHEN the analyzer runs
- THEN expected action items are extracted
- AND each extracted item has evidence.

### Requirement: Evaluation Metrics

The system MUST define evaluation metrics for:

1. action item precision,
2. action item recall,
3. decision precision,
4. decision recall,
5. evidence coverage,
6. schema validation success rate,
7. hallucinated owner rate,
8. tool call success rate.

#### Scenario: Evidence coverage

- GIVEN analyzer outputs for a fixture
- WHEN evaluation runs
- THEN evidence coverage is computed as the percentage of decisions and action items with valid evidence.

### Requirement: No External Credentials in Evaluation

Evaluation MUST run without real Lark credentials, real LLM API keys, Feishu channel connectivity, or nanobot gateway startup.

#### Scenario: CI evaluation

- GIVEN evaluation runs in CI
- WHEN no Lark credentials or LLM keys are configured
- THEN evaluation uses fake provider, fake analyzer, and fixture data.

### Requirement: Regression Tests

The system MUST include regression tests for previously discovered extraction errors.

#### Scenario: Owner hallucination regression

- GIVEN a transcript does not mention an owner
- WHEN analyzer runs
- THEN the owner is not invented
- AND the regression test passes.
