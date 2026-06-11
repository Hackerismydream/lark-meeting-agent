# Live Lark Smoke Results

## Current Status

Status: blocked.

Reason: a real meeting number was provided on 2026-06-11. The first attempt was missing `vc:meeting.bot.join:write`; after that scope was granted, the join API still returned `HTTP 403: no permission`, so the bot could not visibly join the meeting.

## Verified Without Real Lark

- `live-smoke` command exists.
- Missing `--meeting-number` returns a clear `missing_meeting_number` result.
- Dry-run path does not join a meeting.
- Fake approved path runs join, poll, live QA, leave, and can export sanitized raw event shape samples.
- Failure classification covers permission, gray release, bot-not-in-meeting, meeting-ended, no-events, unknown event shape, and page-token issues.

## Real Smoke Evidence

No real join/poll/leave was executed in the original `real-live-meeting-smoke` phase.

2026-06-11 attempts:

- operator: local user account
- provider mode: `cli`
- meeting number: `414 936 709`
- status: `blocked`
- failure class: `permission`
- event count: `0`
- raw shape export: none, because the join did not start
- command after scope grant:

```bash
scripts/lma-real live-smoke \
  --meeting-number 414936709 \
  --approve-visible-join \
  --approve-visible-leave \
  --export-raw-event-shapes /tmp/lma-live-event-shapes-414936709.json
```

Observed first-attempt missing scope:

```text
vc:meeting.bot.join:write
```

Observed second-attempt API error after granting the scope:

```text
HTTP 403: no permission
```

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

## V1.2 Evidence Runner Attempt

2026-06-11:

- meeting number: `909401086`
- provider mode: `cli`
- command: `uv run python scripts/live/run_live_meeting_evidence.py --workspace /Users/martinlos/lark-meeting-agent --meeting-number "909 401 086" --provider-mode cli --out-root runs/live_real --approve-visible-join --approve-visible-leave`
- status: `blocked`
- failure class: `permission`
- event count: `0`
- raw shapes exported: no, because join failed before polling
- dry-run endpoint: `/open-apis/vc/v1/bots/join`
- real API error: `121003 / HTTP 403: no permission`
- evidence pack: `runs/live_real/909401086/` (ignored by git)

This result confirms the local runner, approval boundary, adapter path, audit capture, and blocker reporting. It does not prove live transcript ingestion yet because Feishu rejected the visible join.
