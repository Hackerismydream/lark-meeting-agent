# Tasks: Production Feishu Channel Glue

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/production-feishu-channel-glue/proposal.md`.
- [x] 1.2 Create `openspec/changes/production-feishu-channel-glue/design.md`.
- [x] 1.3 Create `openspec/changes/production-feishu-channel-glue/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate production-feishu-channel-glue`.

## 2. Implementation

- [x] 2.1 Implement requirement: Map Feishu message event to MeetingBotContext: sender_id, chat_id, chat_type, mention state, text, message_id.
- [x] 2.2 Implement requirement: DM can process user-owned requests.
- [x] 2.3 Implement requirement: Group messages require mention or /meeting command.
- [x] 2.4 Implement requirement: allowed_users / allowed_chat_ids / admin_users / write_approvers / live approvers enforced.
- [x] 2.5 Implement requirement: Direct tool approve/live_join/live_leave cannot bypass production policy.
- [x] 2.6 Implement requirement: Approval/reject command UX requires run_id and operation_ids.
- [x] 2.7 Implement requirement: Denied attempts produce safe response and audit.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_production_bot.py`.
- [x] 3.2 Add or update `tests/meeting/test_feishu_channel_glue.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/PRODUCTION_FEISHU_BOT_DEPLOYMENT.md`.
- [x] 4.2 Create or update `docs/PRODUCTION_RUNBOOK.md`.
- [x] 4.3 Create or update `docs/PRODUCTION_BOT_DELIVERY_REPORT.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate production-feishu-channel-glue`.
- [x] 5.5 Write phase delivery report with exact commands and results.
