# Tasks: Production Storage and Run State

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/production-storage-run-state/proposal.md`.
- [x] 1.2 Create `openspec/changes/production-storage-run-state/design.md`.
- [x] 1.3 Create `openspec/changes/production-storage-run-state/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate production-storage-run-state`.

## 2. Implementation

- [x] 2.1 Implement requirement: Repository abstraction is source of truth for production bot process/status/approve/reject.
- [x] 2.2 Implement requirement: SQLite stores runs, write operations, audit events, meetings, segments, minutes, decisions/actions/risks/questions/entity memories.
- [x] 2.3 Implement requirement: Approval executes inside transaction or protected critical section.
- [x] 2.4 Implement requirement: Duplicate approve does not duplicate writes.
- [x] 2.5 Implement requirement: External result IDs/URLs persisted.
- [x] 2.6 Implement requirement: Partial success and needs_reconciliation states supported.
- [x] 2.7 Implement requirement: Schema version/migration metadata exists.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_repository.py`.
- [x] 3.2 Add or update `tests/meeting/test_run_state_recovery.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/STORAGE_RUN_STATE.md`.
- [x] 4.2 Create or update `docs/STORAGE_MIGRATION_PLAN.md`.
- [x] 4.3 Create or update `docs/RUN_RECOVERY_RUNBOOK.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate production-storage-run-state`.
- [x] 5.5 Write phase delivery report with exact commands and results.
