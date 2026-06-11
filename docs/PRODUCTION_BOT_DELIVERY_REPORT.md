# Production Bot Delivery Report

Phase: `production-feishu-channel-glue`

## Implemented

- Added Feishu message payload mapping into `MeetingBotContext`, including sender ID, chat ID, chat type, mention state, text, and message ID.
- Added `handle_feishu_event` as the production bot glue entrypoint.
- Enforced allowed users, allowed chat IDs, admins, write approvers, and live approvers in the production policy.
- Added sanitized denial audit events for unauthorized and non-approver attempts.
- Required production sender context for direct `lark_meeting` `approve`, `live_join`, and `live_leave` actions.
- Kept Lark operations behind `LarkToolAdapter`; this phase did not add any direct Lark SDK, HTTP, or CLI calls.

## Deferred

- Real Feishu channel deployment through `nanobot gateway`.
- Real Feishu app event subscription smoke.
- Production OAPI provider hardening, which is assigned to the next phase.

## Tests Added

- `tests/meeting/test_feishu_channel_glue.py`
- Updates to `tests/meeting/test_production_bot.py`
- Updates to direct `lark_meeting` tool tests for production policy enforcement.

## Validation

Validation commands for this phase:

```bash
uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate production-feishu-channel-glue
```

- compileall: passed
- pytest `tests/meeting`: 96 passed, 5 skipped
- ruff: passed
- OpenSpec: valid

## Real Smoke Status

- Real Lark smoke: not run in this phase.
- Real LLM smoke: not run in this phase.
- Real Feishu channel smoke: not run; requires a configured Feishu app and opt-in runtime.

## Next Phase

Proceed to `oapi-lark-provider`.
