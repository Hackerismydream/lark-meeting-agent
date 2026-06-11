# Proposal: Production Feishu Channel Glue

## Intent

Implement V1.0 phase `production-feishu-channel-glue` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Map Feishu message event to MeetingBotContext: sender_id, chat_id, chat_type, mention state, text, message_id.
- DM can process user-owned requests.
- Group messages require mention or /meeting command.
- allowed_users / allowed_chat_ids / admin_users / write_approvers / live approvers enforced.
- Direct tool approve/live_join/live_leave cannot bypass production policy.

## Scope

This change covers:

- Map Feishu message event to MeetingBotContext: sender_id, chat_id, chat_type, mention state, text, message_id.
- DM can process user-owned requests.
- Group messages require mention or /meeting command.
- allowed_users / allowed_chat_ids / admin_users / write_approvers / live approvers enforced.
- Direct tool approve/live_join/live_leave cannot bypass production policy.
- Approval/reject command UX requires run_id and operation_ids.
- Denied attempts produce safe response and audit.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- Unauthorized user denied.
- Group no mention ignored.
- Non-approver approve denied.
- Approver approve accepted.
- Direct tool approve without context rejected.
- Feishu context mapping tests pass.
