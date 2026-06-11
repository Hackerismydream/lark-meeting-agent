# Run Recovery Runbook

## Status After Restart

Use the production bot command:

```text
/meeting status <run_id>
```

Expected behavior: the bot loads the run from SQLite and returns the stored run snapshot even if `.lark_meeting_agent/run_snapshots/` has been removed.

## Approval After Restart

Use:

```text
/meeting approve <run_id> <operation_id> [operation_id...]
```

Expected behavior:

1. Load the run from SQLite.
2. Enter the repository approval guard.
3. Execute only operations that are not already completed.
4. Persist provider result IDs/URLs.
5. Persist audit events.
6. Save the updated run back to SQLite and JSONL debug files.

## Duplicate Approval

If an approver repeats the same command, completed operations stay completed and are not executed again.

## Failed Write

If a selected write fails:

- the operation is marked `failed`,
- its error is stored,
- the run becomes `partial_success` or `needs_reconciliation`,
- operators should inspect the run and retry only the failed operation after confirming the external system state.
