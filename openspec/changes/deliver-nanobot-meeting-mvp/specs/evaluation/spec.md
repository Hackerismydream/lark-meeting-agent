# Delta for Evaluation

## ADDED Requirements

### Requirement: Fake CI Validation

The repository MUST include tests that pass without real Lark credentials or real LLM credentials.

#### Scenario: Meeting test suite

- GIVEN no external credentials are configured
- WHEN `pytest tests/meeting -q` runs
- THEN meeting schema, normalizer, analyzer, adapter, workflow, memory, and tool tests pass.

### Requirement: Safety Regression Tests

The repository MUST include tests for key safety gates.

Tests MUST cover unknown Lark operation rejection, write without approval rejection, malformed CLI output, secret redaction, no shell invocation, analyzer evidence validation, and prompt-injection write safety.

#### Scenario: Prompt injection fixture

- GIVEN malicious transcript text
- WHEN process runs without explicit send-message request
- THEN no IM write operation is generated.

### Requirement: Real Smoke Paths

The repository MUST document or provide optional real smoke paths for:

1. real LLM dry-run,
2. real lark-cli read dry-run,
3. approval-gated writes after human review.

These smoke paths MUST NOT be required for CI.

#### Scenario: Local real helper

- GIVEN local credentials are configured
- WHEN `scripts/lma-real process ... --dry-run` is run
- THEN it uses real Lark read and real LLM analysis without executing writes.
