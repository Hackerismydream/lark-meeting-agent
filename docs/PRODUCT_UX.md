# Product UX

Lark Meeting Agent uses deterministic meeting workflows with explicit command UX. It does not infer write approval from vague confirmations.

## Response Principles

- Pre-brief, process, live, status, QA, approval, and rejection responses use predictable status labels.
- Dry-run process returns a WritePlan preview and does not write to Lark.
- Approval requires `run_id` plus explicit operation IDs.
- Visible live join/leave require explicit approval flags and live approver/admin policy.
- Insufficient evidence is returned explicitly instead of a fluent unsupported answer.

## Status Labels

- `approval_required`: preview generated or visible live operation requires explicit approval.
- `ok`: read-only command succeeded or approved operation completed.
- `clarification_required`: user sent a vague confirmation without run/operation context.
- `insufficient_evidence`: QA has no source-grounded evidence.
- `denied`: sender is not authorized for the requested action.
- `rejected`: pending writes were rejected.

## Unsafe Confirmation

Messages such as `确认`, `同意`, `批准`, `可以`, `写入`, and `执行` do not approve writes. The user must send:

```text
/meeting approve <run_id> <operation_id> [operation_id...]
```
