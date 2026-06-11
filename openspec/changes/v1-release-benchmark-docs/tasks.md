# Tasks: V1 Release, Benchmark, and Docs

## 1. OpenSpec

- [x] 1.1 Create `openspec/changes/v1-release-benchmark-docs/proposal.md`.
- [x] 1.2 Create `openspec/changes/v1-release-benchmark-docs/design.md`.
- [x] 1.3 Create `openspec/changes/v1-release-benchmark-docs/tasks.md`.
- [x] 1.4 Create required delta specs.
- [x] 1.5 Run `openspec validate v1-release-benchmark-docs`.

## 2. Implementation

- [x] 2.1 Implement requirement: Summarize implemented capabilities without exaggeration.
- [x] 2.2 Implement requirement: Separate fixture metrics, optional LLM metrics, real Lark smoke, blocked/unverified capabilities.
- [x] 2.3 Implement requirement: Provide demo flows: fake lifecycle replay, real live smoke, production bot dry-run, approval demo.
- [x] 2.4 Implement requirement: List V1 known limitations.
- [x] 2.5 Implement requirement: Define V1.1 roadmap: macOS companion app, audio/ASR, richer RAG, production deployment hardening.

## 3. Tests

- [x] 3.1 Add or update `tests/meeting/test_docs_truthfulness.py`.

## 4. Documentation

- [x] 4.1 Create or update `docs/V1_RELEASE_REPORT.md`.
- [x] 4.2 Create or update `docs/V1_BENCHMARK_REPORT.md`.
- [x] 4.3 Create or update `docs/V1_DEMO_RUNBOOK.md`.
- [x] 4.4 Create or update `docs/V1_KNOWN_LIMITATIONS.md`.
- [x] 4.5 Create or update `docs/V1_RESUME_AND_INTERVIEW_NOTES.md`.

## 5. Validation

- [x] 5.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 5.2 Run `uv run python -m pytest tests/meeting -q`.
- [x] 5.3 Run `uv run ruff check nanobot tests`.
- [x] 5.4 Run `openspec validate v1-release-benchmark-docs`.
- [x] 5.5 Write phase delivery report with exact commands and results.
