# Tasks: Real Live Meeting Smoke Gate

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/real-live-meeting-smoke/proposal.md`.
- [x] 1.2 Create `openspec/changes/real-live-meeting-smoke/design.md`.
- [x] 1.3 Create `openspec/changes/real-live-meeting-smoke/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate real-live-meeting-smoke`.

## 2. Implementation

- [x] 2.1 Implement requirement: Add `scripts/lma-real live-smoke` or equivalent command.
- [x] 2.2 Implement requirement: No real Lark smoke in CI by default.
- [x] 2.3 Implement requirement: Require explicit --meeting-number and visible join/leave approval flags.
- [x] 2.4 Implement requirement: Classify failures: permission, gray, not in meeting, meeting ended, no events, unknown event shape, page token issue.
- [x] 2.5 Implement requirement: Record sanitized raw event shape samples when user explicitly requests export.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_real_smoke_scripts.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/LIVE_LARK_SMOKE_RUNBOOK.md`.
- [x] 4.2 Create or update `docs/LIVE_LARK_SMOKE_RESULTS.md`.
- [x] 4.3 Create or update `docs/REAL_LIVE_GATE.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate real-live-meeting-smoke`.
- [x] 5.5 Write phase delivery report with exact commands and results.
