# Live Lark Smoke Runbook

Real live smoke is opt-in and not required for default tests.

## Prerequisites

- `lark-cli` installed.
- User auth is valid.
- Required scopes include `vc:meeting.bot.join:write` and `vc:meeting.meetingevent:read`.
- A currently running meeting exists.
- The operator has the 9-digit meeting number.
- The operator consents that join and leave are visible to participants.

## Commands

```bash
join_json=$(scripts/lma-real live-join \
  --meeting-number <9-digit-meeting-number> \
  --approve-visible-join)
live_run_id=$(printf '%s' "$join_json" | uv run python -c 'import json,sys; print(json.load(sys.stdin)["live_run_id"])')
meeting_id=$(printf '%s' "$join_json" | uv run python -c 'import json,sys; print(json.load(sys.stdin)["meeting_id"])')

scripts/lma-real live-poll \
  --meeting-id "$meeting_id" \
  --live-run-id "$live_run_id"

scripts/lma-real live-qa \
  --live-run-id "$live_run_id" \
  --question "目前有哪些结论和待办？"

scripts/lma-real live-leave \
  --meeting-id "$meeting_id" \
  --approve-visible-leave
```

## Failure Classes

- missing permission,
- not in gray release,
- invalid 9-digit meeting number,
- bot not in meeting,
- meeting ended,
- no transcript event emitted,
- page token issue,
- unknown event shape.

## Pre-Smoke Hardening Checks

Before real smoke, default tests verify:

- invalid meeting numbers are rejected before provider calls,
- meeting passwords/passcodes are redacted in audit events,
- chat events can become source-grounded QA evidence,
- participant/share events enter the live timeline,
- duplicate event ids do not duplicate state,
- page tokens are persisted,
- join/leave without approval are rejected.

Do not fabricate smoke success. If no live meeting is available, record it as not run.
