# Blockers

## Historical Lark Meeting Minutes Gate

Status: optional historical enrichment is blocked by missing readable meeting transcript/minutes data in the currently authorized Feishu/Lark account.

This is no longer the primary product gate. The product direction is live meeting listening: explicitly join an in-progress meeting, poll live meeting events, and build meeting intelligence from the transcript/chat deltas observed while the bot is present.

The repository implementation, OpenSpec delivery changes, fake CI gates, local real-mode helper, DeepSeek real LLM dry-run, lifecycle fake benchmark, and `lark-cli` user authorization are in place.

The project is currently best described as a lifecycle local MVP: live listener is the primary real acquisition path; post-meeting remains the most complete writeback workflow; pre-brief and memory/QA support are implemented through controlled workflows. The project does not claim invisible meeting capture, custom ASR, production OAuth, PostgreSQL/vector DB deployment, or production Feishu rollout.

The remaining external-data limitation is that the currently authorized Feishu/Lark user has meetings visible to `vc +search`, but those meetings do not have readable notes/minute transcript content. `minutes +search` is also authorized and returns zero accessible minute records for the checked date ranges.

Observed command:

```bash
LARK_CLI_NO_PROXY=1 lark-cli vc +search --format json --as user --start 2026-05-01 --end 2026-06-10
```

Observed result:

```text
ok: true
count: 7 visible VC meetings
```

Observed notes command:

```bash
LARK_CLI_NO_PROXY=1 lark-cli vc +notes --format json --as user --meeting-ids <meeting_id>
```

Observed result across the visible meetings:

```text
no notes available for this meeting; no minute file for this meeting
or
no permission to access this meeting's minutes
```

Observed minutes command:

```bash
LARK_CLI_NO_PROXY=1 lark-cli minutes +search --format json --as user --start 2020-01-01 --end 2026-06-10
```

Observed result:

```text
ok: true
count: 0 accessible minute records
```

Historical helper command:

```bash
scripts/lma-real transcript-gate --start 2026-05-01 --end 2026-06-10 --limit 10
```

Current helper result:

```text
status: blocked
visible_meeting_count: 7
accessible_minute_count: 0
checked_meetings: 7
reason: all 1 queries failed
```

## Completed Fixes

- Added `scripts/lma-real` to load the DeepSeek key from macOS Keychain and verify `lark-cli` auth.
- Set `LARK_CLI_NO_PROXY=1` in the helper before credential checks.
- Fixed `CliLarkProvider` to pass `--as user` for meeting read/write commands instead of relying on `defaultAs=auto`.
- Completed user authorization for `vc:meeting.search:read`, `vc:note:read`, `vc:meeting.meetingevent:read`, `vc:record:readonly`, and `minutes:minutes.search:read`.
- Added `minutes.search` support to `CliLarkProvider`.
- Updated the workflow to parse `data.items` and `data.notes` style lark-cli responses and skip visible meetings without transcript content.
- Hardened the LLM analyzer boundary to normalize common real-model JSON deviations while preserving strict internal schemas.
- Verified real DeepSeek dry-run with the transcript fixture.
- Avoided committing authorization URLs, device codes, or secrets.
- Added `docs/LARK_CLI_VERIFICATION_MATRIX.md` to separate adapter implementation from real smoke status.

## Primary Real Gate

To validate the primary real path, start or provide a currently running Feishu/Lark meeting with a 9-digit meeting number, then run:

```bash
scripts/lma-real live-join --meeting-number <9-digit-meeting-number> --approve-visible-join
scripts/lma-real live-poll --meeting-id <returned-long-meeting-id> --live-run-id <returned-live-run-id>
scripts/lma-real live-qa --live-run-id <returned-live-run-id> --question "目前有哪些结论和待办？"
scripts/lma-real live-leave --meeting-id <returned-long-meeting-id> --approve-visible-leave
```

Pass condition:

- the bot visibly joins the meeting,
- `vc.meeting.events` returns live events,
- transcript/chat events are converted into sourced live state,
- live QA cites meeting/segment/speaker/timestamp where available,
- the bot leaves when explicitly approved.

## Optional Historical Enrichment

To test optional historical minutes enrichment, provide or create at least one Feishu/Lark meeting/minute that has readable transcript or minutes content for the authorized user. Then run:

```bash
scripts/lma-real transcript-gate --query "<meeting keyword>"
scripts/lma-real process --latest-ended --query "<meeting keyword>" --create-doc --create-tasks --dry-run
```

Lifecycle pre-brief can be smoke-tested with real `lark-cli` calendar/doc/task reads independently:

```bash
scripts/lma-real prebrief --query "<meeting keyword>" --meeting-type project_sync --project "<project>"
```

## Safest Next Prompt

For the primary live path, tell Codex:

```text
我开了一个正在进行的飞书会议，会议号是 <9位会议号>，继续 live listener gate
```

Codex should then run the real visible join, event poll, live QA, leave flow, update the live listener evidence docs/tasks, commit the evidence update, and push the branch.
