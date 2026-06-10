# Historical Transcript Gate

This gate now covers optional historical transcript/minutes enrichment only. The primary product gate is live meeting listening; see `docs/LIVE_MEETING_LISTENER.md`.

Current historical status: blocked by account data. The local `lark-cli` auth and meeting search path work, but the current account has no readable meeting minutes/transcript content for checked meetings.

## Verification Steps

Run:

```bash
scripts/lma-real status
```

Then verify meeting search:

```bash
LARK_CLI_NO_PROXY=1 lark-cli vc +search --format json --as user --start 2026-05-01 --end 2026-06-10
```

Try notes for a selected meeting:

```bash
LARK_CLI_NO_PROXY=1 lark-cli vc +notes --format json --as user --meeting-ids <meeting_id>
```

Try minutes search:

```bash
LARK_CLI_NO_PROXY=1 lark-cli minutes +search --format json --as user --start 2020-01-01 --end 2026-06-10
```

Historical pass condition:

- At least one command returns readable transcript/minutes text that can be normalized.

Historical blocked condition:

- Meetings are visible, but notes/minutes return no notes, no minute file, no permission, or zero accessible minute records.

## Dry-run After Gate Passes

Once a readable meeting exists:

```bash
scripts/lma-real process --latest-ended --query "<meeting keyword>" --create-doc --create-tasks --dry-run
```

Expected result:

- run status is `approval_required`,
- minutes are generated,
- decisions and action items have grounded evidence,
- write operations remain pending,
- no Lark write executes.

## Notes

Do not treat missing readable minutes as a code failure if auth/search paths work. It only blocks optional historical enrichment. Record the account-data limitation in `docs/BLOCKERS.md` and use the live listener gate as the primary real validation path.
