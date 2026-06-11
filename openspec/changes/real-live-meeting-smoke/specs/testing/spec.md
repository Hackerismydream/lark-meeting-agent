# Delta for Testing in Real Live Meeting Smoke Gate

## ADDED Requirements

### Requirement: Tests for real-live-meeting-smoke

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
