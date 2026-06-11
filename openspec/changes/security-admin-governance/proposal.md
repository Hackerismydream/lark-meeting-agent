# Proposal: Security, Admin, and Governance

## Intent

Implement V1.0 phase `security-admin-governance` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Add admin config validation: no wildcard allowFrom by default, exec disabled, workspace restricted, approvers configured, audit enabled.
- Separate permissions: can_use_bot, can_process, can_approve_writes, can_live_join, can_live_leave, can_admin.
- Prompt injection across transcript/chat/shared docs cannot trigger tools.
- Direct lark-cli bypass absent.
- Secrets redacted from logs/audit/docs.

## Scope

This change covers:

- Add admin config validation: no wildcard allowFrom by default, exec disabled, workspace restricted, approvers configured, audit enabled.
- Separate permissions: can_use_bot, can_process, can_approve_writes, can_live_join, can_live_leave, can_admin.
- Prompt injection across transcript/chat/shared docs cannot trigger tools.
- Direct lark-cli bypass absent.
- Secrets redacted from logs/audit/docs.
- Data retention and deletion policy documented.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- Security tests pass.
- Red-team fixtures do not cause tool calls.
- Production config warnings are actionable.
- Docs distinguish demo config and production config.
