# Tasks: Harden Live Listener Before Real Smoke

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/harden-live-listener-real-smoke/proposal.md`.
- [x] 1.2 Create `openspec/changes/harden-live-listener-real-smoke/design.md`.
- [x] 1.3 Create `openspec/changes/harden-live-listener-real-smoke/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate harden-live-listener-real-smoke`.

## 2. Implementation

- [x] 2.1 Implement requirement: Validate meeting_number as exactly 9 digits before real join.
- [x] 2.2 Implement requirement: Redact password/passcode/meeting_password from logs and audit.
- [x] 2.3 Implement requirement: Map chat_received/message_received to live state sources, not marker-only events.
- [x] 2.4 Implement requirement: Track participant and share events in live timeline.
- [x] 2.5 Implement requirement: Persist and reuse page_token / next_page_token.
- [x] 2.6 Implement requirement: Deduplicate event_id across repeated polls.
- [x] 2.7 Implement requirement: Handle has_more explicitly.
- [x] 2.8 Implement requirement: Ensure live join/leave cannot bypass production access policy.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_live_lark_listener.py`.
- [x] 3.2 Add or update `tests/meeting/test_live_listener_hardening.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/LIVE_MEETING_LISTENER.md`.
- [x] 4.2 Create or update `docs/LIVE_LARK_SMOKE_RUNBOOK.md`.
- [x] 4.3 Create or update `docs/LIVE_LISTENER_HARDENING_REPORT.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate harden-live-listener-real-smoke`.
- [x] 5.5 Write phase delivery report with exact commands and results.
