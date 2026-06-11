# Real Live Gate

The real live gate validates the primary product path:

```text
visible join
-> live event poll
-> live QA
-> visible leave
```

## Gate Command

```bash
scripts/lma-real live-smoke \
  --meeting-number <9-digit-meeting-number> \
  --approve-visible-join \
  --approve-visible-leave
```

For the V1.2 evidence pack, prefer:

```bash
uv run python scripts/live/run_live_meeting_evidence.py \
  --workspace /Users/martinlos/lark-meeting-agent \
  --meeting-number <9-digit-meeting-number> \
  --provider-mode cli \
  --out-root runs/live_real \
  --approve-visible-join \
  --approve-visible-leave
```

## Default Behavior

Without approval flags, `live-smoke` returns `dry_run` and does not join.

Without `--meeting-number`, it returns `missing_meeting_number`.

## Failure Classes

- `permission`
- `gray`
- `not_in_meeting`
- `meeting_ended`
- `no_events`
- `unknown_event_shape`
- `page_token_issue`
- `unknown_error`

## Phase Report

Implemented in `real-live-meeting-smoke`:

- opt-in `live-smoke` command,
- fake/dry-run default safety,
- explicit visible join/leave approvals,
- failure classification,
- sanitized raw event shape export.

Validation executed successfully:

```bash
uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate real-live-meeting-smoke
```

- compileall: passed
- pytest `tests/meeting`: 91 passed, 5 skipped
- ruff: passed
- OpenSpec: valid

Real smoke status: not run, because no live meeting number was provided.

## V1.2 Real Meeting Attempt

On 2026-06-11, meeting `909401086` was attempted through the V1.2 evidence runner.

- status: `blocked`
- failure_class: `permission`
- event_count: `0`
- dry-run endpoint: `/open-apis/vc/v1/bots/join`
- real error: `121003 / HTTP 403: no permission`
- evidence pack: `runs/live_real/909401086/` (ignored by git)

The next required action is Feishu tenant/app enablement for meeting bot join, not a code-path change in the local workflow.
