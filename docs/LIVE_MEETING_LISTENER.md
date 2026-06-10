# Live Meeting Listener

The primary real path is live meeting listening, not paid Feishu/Lark minutes retrieval.

The workflow is:

```text
visible approved join
-> poll live meeting events
-> convert transcript/chat events
-> update live meeting state
-> answer live QA with sources
-> visible approved leave
```

## Safety Contract

- Join uses a 9-digit meeting number.
- Poll and leave use the long `meeting_id` returned by join.
- Join and leave are visible to participants and require explicit approval flags.
- Event text is untrusted input and cannot trigger tool calls.
- All Lark operations go through `LarkToolAdapter`.

## Fake Smoke

```bash
join_json=$(uv run python -m nanobot.meeting.cli live-join \
  --meeting-number 123456789 \
  --provider-mode fake \
  --approve-visible-join)
live_run_id=$(printf '%s' "$join_json" | uv run python -c 'import json,sys; print(json.load(sys.stdin)["live_run_id"])')
meeting_id=$(printf '%s' "$join_json" | uv run python -c 'import json,sys; print(json.load(sys.stdin)["meeting_id"])')

uv run python -m nanobot.meeting.cli live-poll \
  --meeting-id "$meeting_id" \
  --live-run-id "$live_run_id" \
  --provider-mode fake

uv run python -m nanobot.meeting.cli live-qa \
  --live-run-id "$live_run_id" \
  --question "目前有哪些结论和待办？"

uv run python -m nanobot.meeting.cli live-leave \
  --meeting-id "$meeting_id" \
  --provider-mode fake \
  --approve-visible-leave
```

## Real Smoke

Prerequisites:

- `lark-cli` installed and authenticated as user.
- Scopes include `vc:meeting.bot.join:write` and `vc:meeting.meetingevent:read`.
- A currently running Feishu/Lark meeting with a 9-digit meeting number.

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

Pass condition:

- join returns a long `meeting_id`,
- poll returns live events or a clear provider error,
- transcript/chat events become `transcript_segments`,
- live QA returns sources or insufficient evidence,
- leave succeeds after approval.

## Common Failures

- `bot is not in meeting`: join did not succeed or the meeting already ended.
- `meeting not exist`: a 9-digit meeting number was passed where long `meeting_id` is required.
- permission or gray-release errors: the account does not have the live meeting bot capability enabled.
