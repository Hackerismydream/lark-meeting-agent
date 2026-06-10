# Tasks: Testing Strategy and Live Meeting Simulator

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/testing-strategy-live-simulator/proposal.md`.
- [x] 1.2 Create `openspec/changes/testing-strategy-live-simulator/design.md`.
- [x] 1.3 Create `openspec/changes/testing-strategy-live-simulator/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate testing-strategy-live-simulator`.

## 2. Implementation

- [x] 2.1 Implement requirement: Adopt text/event-first as primary development and evaluation path.
- [x] 2.2 Implement requirement: Build a LiveMeetingSimulator that emits Lark-like event pages with has_more/page_token.
- [x] 2.3 Implement requirement: Support transcript, chat, participant, share, malformed, duplicate, out-of-order, and prompt-injection events.
- [x] 2.4 Implement requirement: Create 8 scenario fixtures covering customer, project weekly, requirement review, tech review, incident, 1:1, sales/CS, long retrospective.
- [x] 2.5 Implement requirement: Implement live and lifecycle replay with metrics JSON and failures JSON.
- [x] 2.6 Implement requirement: Add Hypothesis for event conversion fuzzing and Freezegun for time tests.
- [x] 2.7 Implement requirement: Keep real Lark and real LLM tests opt-in only.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_live_simulator.py`.
- [x] 3.2 Add or update `tests/meeting/test_live_event_replay.py`.
- [x] 3.3 Add or update `tests/meeting/test_event_conversion_contract.py`.
- [x] 3.4 Add or update `tests/meeting/test_event_conversion_fuzz.py`.
- [x] 3.5 Add or update `tests/meeting/test_lifecycle_replay.py`.
- [x] 3.6 Add or update `tests/meeting/test_prebrief_scenarios.py`.
- [x] 3.7 Add or update `tests/meeting/test_postmeeting_scenarios.py`.
- [x] 3.8 Add or update `tests/meeting/test_qa_source_metrics.py`.
- [x] 3.9 Add or update `tests/meeting/test_tool_safety_matrix.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/TESTING_STRATEGY.md`.
- [x] 4.2 Create or update `docs/FIXTURE_GUIDE.md`.
- [x] 4.3 Create or update `docs/LIVE_SIMULATOR.md`.
- [x] 4.4 Create or update `docs/EVALUATION_METRICS.md`.
- [x] 4.5 Create or update `docs/LIVE_LARK_SMOKE_RUNBOOK.md`.
- [x] 4.6 Create or update `docs/ASR_TESTING.md`.
- [x] 4.7 Create or update `docs/OSS_TOOLING_DECISIONS.md`.
- [x] 4.8 Create or update `docs/TESTING_INFRA_DELIVERY_REPORT.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate testing-strategy-live-simulator`.
- [x] 5.5 Write phase delivery report with exact commands and results.
