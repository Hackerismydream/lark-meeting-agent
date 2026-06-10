# Tasks: Add Real Transcript Gate Helper

## 1. OpenSpec

- [x] 1.1 Create proposal, design, tasks, and delta specs.
- [x] 1.2 Validate `openspec validate add-real-transcript-gate-helper`.

## 2. Tests First

- [x] 2.1 Add failing tests for ready transcript gate report.
- [x] 2.2 Add failing tests for blocked transcript gate report.
- [x] 2.3 Add failing test for CLI command output.

## 3. Implementation

- [x] 3.1 Add transcript gate schemas.
- [x] 3.2 Implement read-only `TranscriptGateWorkflow`.
- [x] 3.3 Add `transcript-gate` CLI command.
- [x] 3.4 Add `scripts/lma-real transcript-gate` route.
- [x] 3.5 Update blocker/runbook docs.

## 4. Validation

- [x] 4.1 Run `uv run python -m pytest tests/meeting -q`.
- [x] 4.2 Run `uv run ruff check nanobot tests`.
- [x] 4.3 Run `openspec validate add-real-transcript-gate-helper`.
- [x] 4.4 Run `scripts/lma-real transcript-gate --help`.
