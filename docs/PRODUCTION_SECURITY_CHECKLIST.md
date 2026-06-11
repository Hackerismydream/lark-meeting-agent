# Production Security Checklist

Use this checklist before running Lark Meeting Agent as a production Feishu bot.

## Access Control

- [ ] Feishu channel `allowFrom` is explicit.
- [ ] Group policy is `mention` or stricter.
- [ ] Meeting-agent allowed users are configured.
- [ ] Allowed chat IDs are configured for group use.
- [ ] Admin users are explicit.
- [ ] Processing users are explicit when different from allowed users.
- [ ] Write approvers are explicit.
- [ ] Live join approvers are explicit.
- [ ] Live leave approvers are explicit.
- [ ] Non-approvers cannot approve write operations.
- [ ] Denied access attempts are audited without leaking secrets.

## Tool Boundary

- [ ] All Lark operations go through `LarkToolAdapter`.
- [ ] Workflows do not call `lark-cli`, HTTP APIs, SDKs, or shell directly.
- [ ] Unknown operations are rejected.
- [ ] Read and write operations are classified.
- [ ] `docs.create`, `task.create`, and `im.send` require approval.
- [ ] `process` never executes writes.
- [ ] Duplicate approve does not duplicate writes.

## Runtime Safety

- [ ] `tools.exec.enable=false` in production unless explicitly justified.
- [ ] `tools.restrictToWorkspace=true`.
- [ ] `meetingAgent.audit.enabled=true`.
- [ ] Shell access is not used for Lark operations.
- [ ] Secrets are provided through env vars or a secret manager.
- [ ] No secrets are committed to docs, tests, fixtures, logs, traces, or config.
- [ ] Run trace redaction is enabled.

## Approval Protocol

- [ ] Bot response includes run ID.
- [ ] Bot response includes operation IDs.
- [ ] Bot response states no writes have executed yet.
- [ ] Approval command requires explicit operation IDs.
- [ ] Reject command marks pending operations rejected.
- [ ] Unknown operation IDs are rejected or ignored safely.
- [ ] Provider mode is bound to run snapshot.

## Data and Storage

- [ ] Production storage backend is configured.
- [ ] Approval state persists across restarts.
- [ ] Audit events persist across restarts.
- [ ] Storage transactions protect approval state changes.
- [ ] Data retention period is documented.
- [ ] Deletion procedure is documented and tested.
- [ ] JSONL local backend remains for dev/test only unless explicitly selected.

## Demo vs Production

Demo config may use fake providers, local JSONL, and fixture transcripts. Production config must use explicit users/chats, audit enabled, workspace restriction, disabled generic exec, and SQLite or a later approved production store.

## Real Lark Gate

- [ ] `auth.status` passes.
- [ ] `vc.search` or `minutes.search` returns accessible records.
- [ ] At least one meeting has readable transcript/minutes content.
- [ ] Dry-run write command paths are verified.
- [ ] Real writes are tested only with safe explicit targets.
