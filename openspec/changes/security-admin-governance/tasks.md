# Tasks: Security, Admin, and Governance

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/security-admin-governance/proposal.md`.
- [x] 1.2 Create `openspec/changes/security-admin-governance/design.md`.
- [x] 1.3 Create `openspec/changes/security-admin-governance/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate security-admin-governance`.

## 2. Implementation

- [x] 2.1 Implement requirement: Add admin config validation: no wildcard allowFrom by default, exec disabled, workspace restricted, approvers configured, audit enabled.
- [x] 2.2 Implement requirement: Separate permissions: can_use_bot, can_process, can_approve_writes, can_live_join, can_live_leave, can_admin.
- [x] 2.3 Implement requirement: Prompt injection across transcript/chat/shared docs cannot trigger tools.
- [x] 2.4 Implement requirement: Direct lark-cli bypass absent.
- [x] 2.5 Implement requirement: Secrets redacted from logs/audit/docs.
- [x] 2.6 Implement requirement: Data retention and deletion policy documented.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_security_governance.py`.
- [x] 3.2 Add or update `tests/meeting/test_red_team_cases.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/PRODUCTION_SECURITY_CHECKLIST.md`.
- [x] 4.2 Create or update `docs/ADMIN_GUIDE.md`.
- [x] 4.3 Create or update `docs/RED_TEAM_CASES.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate security-admin-governance`.
- [x] 5.5 Write phase delivery report with exact commands and results.
