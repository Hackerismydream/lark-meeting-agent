# Tasks: Observability and Reliability

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/observability-reliability/proposal.md`.
- [x] 1.2 Create `openspec/changes/observability-reliability/design.md`.
- [x] 1.3 Create `openspec/changes/observability-reliability/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate observability-reliability`.

## 2. Implementation

- [x] 2.1 Implement requirement: Every workflow node emits trace event.
- [x] 2.2 Implement requirement: Every Lark tool call emits audit event.
- [x] 2.3 Implement requirement: Error taxonomy covers permission, gray, missing transcript, unknown event, malformed output, approval mismatch, provider mismatch.
- [x] 2.4 Implement requirement: Metrics include latency, event count, conversion count, tool success, approval count, failures.
- [x] 2.5 Implement requirement: OpenTelemetry/Phoenix documented as optional, not mandatory dependency.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_observability.py`.
- [x] 3.2 Add or update `tests/meeting/test_error_taxonomy.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/OBSERVABILITY.md`.
- [x] 4.2 Create or update `docs/ERROR_TAXONOMY.md`.
- [x] 4.3 Create or update `docs/RELIABILITY_RUNBOOK.md`.
- [x] 4.4 Create or update `docs/SMOKE_REPORT_TEMPLATE.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate observability-reliability`.
- [x] 5.5 Write phase delivery report with exact commands and results.
