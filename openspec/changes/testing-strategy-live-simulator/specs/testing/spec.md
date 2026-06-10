# Delta for Testing in Testing Strategy and Live Meeting Simulator

## ADDED Requirements

### Requirement: Tests for testing-strategy-live-simulator

The phase MUST include tests covering its expected behavior.

#### Scenario: Default test environment

- GIVEN no real Lark credentials
- AND no real LLM API key
- WHEN tests run
- THEN tests pass using fake providers, fixtures, or skipped opt-in tests.

#### Scenario: Real smoke opt-in

- GIVEN real Lark or real LLM credentials are unavailable
- WHEN tests run
- THEN real smoke tests are skipped
- AND the skip reason is clear.
