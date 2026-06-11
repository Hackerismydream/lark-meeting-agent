# Live Lark Smoke Results

## Current Status

Status: not run.

Reason: no currently running Feishu/Lark meeting number was provided during the `real-live-meeting-smoke` phase.

## Verified Without Real Lark

- `live-smoke` command exists.
- Missing `--meeting-number` returns a clear `missing_meeting_number` result.
- Dry-run path does not join a meeting.
- Fake approved path runs join, poll, live QA, leave, and can export sanitized raw event shape samples.
- Failure classification covers permission, gray release, bot-not-in-meeting, meeting-ended, no-events, unknown event shape, and page-token issues.

## Real Smoke Evidence

No real join/poll/leave was executed in this phase.

When a running meeting is available, run:

```bash
scripts/lma-real live-smoke \
  --meeting-number <9-digit-meeting-number> \
  --approve-visible-join \
  --approve-visible-leave \
  --export-raw-event-shapes /tmp/lma-live-event-shapes.json
```

Record the result here with:

- timestamp,
- operator,
- provider mode,
- status,
- failure class if blocked,
- event count,
- whether raw shapes were exported,
- confirmation that no secrets or private transcript content were committed.
