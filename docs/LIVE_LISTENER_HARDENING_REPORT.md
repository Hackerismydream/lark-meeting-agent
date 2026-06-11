# Live Listener Hardening Report

## Phase

`harden-live-listener-real-smoke`

## Implemented

- Validates live meeting numbers as exactly 9 digits before calling any provider.
- Redacts `password`, `passcode`, and `meeting_password` fields from adapter audit data.
- Maps `chat_received` and `message_received` text into source-grounded live transcript state.
- Tracks participant, share, marker, chat, and transcript events in live state timeline.
- Persists `page_token` / `next_page_token` and `has_more` onto live state.
- Deduplicates repeated `event_id` values in `LiveMeetingWorkflow`.
- Keeps join and leave approval-gated through `LarkToolAdapter`.
- Confirms production bot policy denies untrusted live-join attempts before routing.

## Deferred

- Real live smoke. No running 9-digit meeting number was provided for this phase.
- Production Feishu command UX for live join/poll/leave. That belongs to `production-feishu-channel-glue`.

## Tests Added

- `tests/meeting/test_live_listener_hardening.py`
- Updates to `tests/meeting/test_live_lark_listener.py` behavior through shared live workflow state.

## Validation Commands

Executed successfully:

```bash
uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate harden-live-listener-real-smoke
```

Results:

- compileall: passed
- pytest `tests/meeting`: 86 passed, 5 skipped
- ruff: passed
- OpenSpec: valid

## Real Smoke

Not run. This phase is fake/simulator-compatible hardening before the real live meeting smoke phase.

## Next Phase

`real-live-meeting-smoke`
