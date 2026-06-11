# V1 Demo Runbook

## Fake Lifecycle Replay

```bash
uv run python -m nanobot.meeting.cli evaluate \
  --cases tests/fixtures/meeting/evaluation/lifecycle_cases.json \
  --output /tmp/lma-v1-lifecycle-eval.json
```

## Fake Production Bot Dry Run

Use `/meeting process Alpha` through the production bot wrapper or `lark_meeting(action="bot_message", ...)`.

Expected:

- status: `approval_required`,
- no write executed,
- response includes `run_id`,
- response includes operation IDs.

## Approval Demo

```text
/meeting status
/meeting approve <run_id> <operation_id>
```

Expected:

- only selected operation IDs execute,
- duplicate approve does not duplicate completed operations,
- audit events persist.

## Real Live Smoke

Requires a currently running Lark meeting and explicit visible approval:

```bash
scripts/lma-real live-smoke \
  --meeting-number <9-digit-meeting-number> \
  --approve-visible-join \
  --approve-visible-leave
```

If no real meeting number or tenant scope is available, record the blocker instead of claiming success.

## Production Feishu Channel Smoke

Not part of normal tests. Requires configured Feishu app, event subscription, allowed users/chats, and opt-in runtime.
