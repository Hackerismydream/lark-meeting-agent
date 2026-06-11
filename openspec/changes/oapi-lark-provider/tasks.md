# Tasks: Production Lark OpenAPI Provider

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/oapi-lark-provider/proposal.md`.
- [x] 1.2 Create `openspec/changes/oapi-lark-provider/design.md`.
- [x] 1.3 Create `openspec/changes/oapi-lark-provider/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate oapi-lark-provider`.

## 2. Implementation

- [x] 2.1 Implement requirement: Preserve LarkToolAdapter interface.
- [x] 2.2 Implement requirement: Add OapiLarkProvider for production path.
- [x] 2.3 Implement requirement: Support minimal operations: auth/status equivalent, calendar.agenda or minutes/vc search, docs.create, task.create, im.send where feasible.
- [x] 2.4 Implement requirement: Real tests opt-in only.
- [x] 2.5 Implement requirement: HTTP/API tests may use fake responses or recorded sanitized fixtures.
- [x] 2.6 Implement requirement: Token and secret redaction required.
- [x] 2.7 Implement requirement: Provider errors classified: missing scope, invalid token, permission denied, rate limit, unavailable.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_oapi_lark_provider.py`.
- [x] 3.2 Add or update `tests/meeting/test_lark_adapter.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/OAPI_PROVIDER_PLAN.md`.
- [x] 4.2 Create or update `docs/OAPI_PROVIDER_DELIVERY_REPORT.md`.
- [x] 4.3 Create or update `docs/LARK_PROVIDER_STRATEGY.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate oapi-lark-provider`.
- [x] 5.5 Write phase delivery report with exact commands and results.
