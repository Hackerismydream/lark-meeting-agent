# Production Runbook

This runbook is the operating guide for the future production Feishu bot.

## Status

Current status: production Feishu channel glue is implemented and fake-tested. Real Feishu channel deployment remains opt-in and unverified until a configured Feishu app is smoke-tested.

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

## Access Policy

Production policy is evaluated before any meeting workflow runs.

- DM messages can run user-owned requests when the sender is in `allowed_users`, `admin_users`, or the relevant approver set.
- Group messages require either an explicit bot mention or a `/meeting` command.
- Group chat IDs can be allowlisted with `allowed_chat_ids`.
- Write approval requires `write_approvers` or `admin_users`.
- Visible live join/leave requires `live_approvers` or `admin_users`.
- Denied attempts return a generic safe response and write a sanitized audit event.

## Dry-run Process

Local transcript gate:

```bash
scripts/lma-real transcript-gate --query "<meeting keyword>"
```

Only continue to processing when the gate reports `ready`.

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
- Direct `lark_meeting(action="approve")` calls without sender context are rejected.

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

### Live control denied

Meaning: sender tried to visibly join or leave a meeting without live approver/admin policy.

Action:

1. Confirm the sender is an intended live meeting operator.
2. Add sender to live approvers if intended.
3. Retry with explicit visible join/leave approval.

### Write rejected

Meaning: approval missing, operation unknown, operation already completed, provider mismatch, or global writes disabled.

Action:

1. Inspect run status.
2. Inspect WritePlan operation IDs.
3. Confirm approver permissions.
4. Confirm write mode is enabled.
