# Admin Guide

## Required Production Config

Production administrators must configure:

- explicit Feishu `allowFrom`,
- mention-scoped group policy,
- `tools.exec.enable=false`,
- `tools.restrictToWorkspace=true`,
- `meetingAgent.writeApprovers`,
- `meetingAgent.audit.enabled=true`,
- storage backend and retention policy.

Use `validate_admin_config` to check config before rollout. Findings include an action field so each warning is directly fixable.

## Permission Model

Permissions are separated:

- `can_use_bot`
- `can_process`
- `can_approve_writes`
- `can_live_join`
- `can_live_leave`
- `can_admin`

Admins inherit operational permissions. Write approvers do not automatically become live meeting operators unless also configured for live control.

## Data Retention

Recommended default:

- keep SQLite run/audit records for 90 days,
- keep local JSONL debug exports only in development,
- delete exported live raw event shape files after smoke analysis,
- do not store secrets in logs, traces, docs, fixtures, or reports.

## Deletion Procedure

1. Identify the run or meeting ID.
2. Export any required audit evidence to the approved retention system.
3. Delete matching rows from SQLite tables.
4. Delete matching `.lark_meeting_agent` snapshots, traces, and JSONL records if debug export exists.
5. Re-run status/QA checks to confirm deleted content is no longer available.

The current MVP documents deletion policy but does not yet ship an admin deletion CLI.
