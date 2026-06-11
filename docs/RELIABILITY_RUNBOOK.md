# Reliability Runbook

## Trace Reconstruction

Load a trace by run ID:

```python
from nanobot.meeting.tracing import TraceReader

trace = TraceReader(".").load("<run_id>")
```

The trace should show each workflow stage and enough counts to reconstruct where the run stopped.

## Audit Inspection

Inspect adapter audit events for failed Lark operations. Failures are classified by `execution_status` and provider error text, with secrets redacted.

## Partial Success

If a run is `partial_success`, some writes completed and at least one failed. Do not blindly replay all operations. Inspect the failed operation IDs and external system state first.

## Needs Reconciliation

If a run is `needs_reconciliation`, selected writes failed and none completed. Confirm target docs/tasks/messages before retrying.

## Smoke Reports

Every real smoke must record:

- date/time,
- provider mode,
- identity used,
- real Lark/LLM credentials present or blocked,
- exact commands,
- sanitized result,
- unverified claims,
- blockers and next action.
