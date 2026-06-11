# Tasks: Lifecycle Product UX

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/lifecycle-product-ux/proposal.md`.
- [x] 1.2 Create `openspec/changes/lifecycle-product-ux/design.md`.
- [x] 1.3 Create `openspec/changes/lifecycle-product-ux/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate lifecycle-product-ux`.

## 2. Implementation

- [x] 2.1 Implement requirement: Define canonical commands and Chinese aliases.
- [x] 2.2 Implement requirement: Process/prebrief/live/status/qa approval flow has predictable responses.
- [x] 2.3 Implement requirement: Approval prompt is safe and explicit.
- [x] 2.4 Implement requirement: Status without run_id can show recent pending runs for authorized user/chat.
- [x] 2.5 Implement requirement: No vague '确认' auto-approves without explicit run/operation context.
- [x] 2.6 Implement requirement: User messages distinguish dry-run, approved, rejected, failed, insufficient evidence.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_product_ux_commands.py`.
- [x] 3.2 Add or update `tests/meeting/test_snapshots.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/PRODUCT_UX.md`.
- [x] 4.2 Create or update `docs/COMMANDS.md`.
- [x] 4.3 Create or update `docs/DEMO_RUNBOOK.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate lifecycle-product-ux`.
- [x] 5.5 Write phase delivery report with exact commands and results.
