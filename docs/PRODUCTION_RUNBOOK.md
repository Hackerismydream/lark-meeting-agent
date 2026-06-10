# Production Runbook

This runbook is the operating guide for the future production Feishu bot.

## Status

Current status: production bot documentation/spec stage. The existing implementation remains a lifecycle local MVP.

## Health Check

Local auth and diagnostic check:

```bash
scripts/lma-real status
```

Production target health checks:

```text
/meeting status
```

The bot should return provider, storage, write-mode, and transcript-gate status without printing secrets.

## Dry-run Process

Target DM command:

```text
/meeting process
```

Expected behavior:

1. Resolve latest ended meeting or report transcript blocker.
2. Generate structured minutes.
3. Generate WritePlan.
4. Return approval prompt.
5. Execute no writes.

## Approval

Target command:

```text
/meeting approve <run_id> <operation_id> [operation_id...]
```

Rules:

- Sender must be a write approver or admin.
- Operation IDs must exist in the run's WritePlan.
- Completed operations must not execute again.
- Provider mode comes from the run snapshot unless explicit override is implemented and authorized.

## Rejection

Target command:

```text
/meeting reject <run_id>
```

Expected behavior:

- Pending operations are marked rejected.
- No Lark write executes.
- Audit records the rejection.

## Disable Writes

Production config must support a global dry-run or writes-disabled mode.

Expected behavior when writes are disabled:

- Process can still generate WritePlan previews.
- Approve commands are rejected with a safe message.
- No `docs.create`, `task.create`, or `im.send` executes.

## Common Errors

### No readable transcript

Meaning: account can see the meeting but cannot read notes/minutes.

Action:

1. Check `docs/REAL_TRANSCRIPT_GATE.md`.
2. Confirm the meeting has generated minutes.
3. Confirm the authorized user has permission.
4. Re-run transcript gate verification.

### User denied

Meaning: sender is not allowed by channel config or meeting-agent policy.

Action:

1. Check Feishu `allowFrom`.
2. Check meeting-agent allowed users/admins.
3. Check group chat ID policy.

### Approval denied

Meaning: sender can use the bot but is not a write approver.

Action:

1. Add sender to write approvers if intended.
2. Retry explicit approve command.

### Write rejected

Meaning: approval missing, operation unknown, operation already completed, provider mismatch, or global writes disabled.

Action:

1. Inspect run status.
2. Inspect WritePlan operation IDs.
3. Confirm approver permissions.
4. Confirm write mode is enabled.
