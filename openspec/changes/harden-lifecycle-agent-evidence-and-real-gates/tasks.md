## 1. OpenSpec

- [x] 1.1 Create proposal, design, specs, and tasks for `harden-lifecycle-agent-evidence-and-real-gates`.
- [x] 1.2 Validate `openspec validate harden-lifecycle-agent-evidence-and-real-gates`.
- [x] 1.3 Commit planning artifacts.

## 2. Evidence Integrity

- [ ] 2.1 Add `EvidenceValidationError`.
- [ ] 2.2 Add `EvidenceIntegrityValidator` for minutes and transcript segments.
- [ ] 2.3 Integrate validation into LLM analyzer parse path and `PostMeetingWorkflow`.
- [ ] 2.4 Add tests for valid evidence, unknown segment, invented quote backfill, and optional evidence validation.

## 3. Provider Binding and Idempotency

- [ ] 3.1 Extend `Run` with provider/analyzer/write-plan/approval metadata while preserving old snapshot loading.
- [ ] 3.2 Extend `WriteOperation` with stable idempotency key.
- [ ] 3.3 Update write plan builder to generate idempotency keys.
- [ ] 3.4 Update approve to use stored provider mode, reject mismatch without override, and skip already completed operations.
- [ ] 3.5 Update CLI approve override behavior and tests.

## 4. Evaluation Split

- [ ] 4.1 Rename current report profile to deterministic fixture regression.
- [ ] 4.2 Add optional LLM extraction benchmark fixtures.
- [ ] 4.3 Add skipped real-LLM benchmark tests gated by `RUN_REAL_LLM_TESTS=1`.
- [ ] 4.4 Update evaluation docs with exact metric scope.

## 5. Lark CLI Verification and Docs

- [ ] 5.1 Add `docs/LARK_CLI_VERIFICATION_MATRIX.md`.
- [ ] 5.2 Update README and project docs for lifecycle MVP truthfulness.
- [ ] 5.3 Update blocker and delivery reports with real gate and benchmark wording.

## 6. Validation and Commit

- [ ] 6.1 Run `uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [ ] 6.2 Run `uv run python -m pytest tests/meeting -q`.
- [ ] 6.3 Run `uv run ruff check nanobot tests`.
- [ ] 6.4 Run `openspec validate harden-lifecycle-agent-evidence-and-real-gates`.
- [ ] 6.5 Run `scripts/lma-real status`.
- [ ] 6.6 Commit implementation and push `main`.
