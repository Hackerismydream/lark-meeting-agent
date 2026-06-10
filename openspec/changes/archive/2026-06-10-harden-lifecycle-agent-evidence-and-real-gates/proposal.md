## Why

The lifecycle implementation now covers pre-brief, live transcript/event understanding, post-meeting write plans, memory, retrieval, and evaluation, but its strongest public claims still depend on hardening: evidence references must be grounded in real transcript segments, approved writes must be provider-bound and idempotent, Lark CLI support must be documented honestly, and benchmark metrics must distinguish deterministic fixtures from real LLM extraction.

This change improves trustworthiness without adding broad new product surface.

## What Changes

- Add transcript-grounded evidence integrity validation for `MeetingMinutes`.
- Bind `approve` execution to the provider mode stored in the original run snapshot.
- Add write operation idempotency keys and prevent duplicate execution on repeated approvals.
- Split evaluation terminology into deterministic fixture regression and optional LLM extraction benchmark.
- Add a real `lark-cli` verification matrix that records implemented, tested, verified, blocked, and unverified operations without fabricating status.
- Update docs so lifecycle local MVP, post-meeting closed-loop maturity, fixture metrics, and real Lark blockers are described consistently.

## Capabilities

### New Capabilities

- `evidence-integrity`: Validate that evidence refs point to real transcript segments and do not preserve model-invented quotes.
- `write-idempotency`: Bind approval to run snapshot provider mode and prevent duplicate writes.
- `lark-cli-verification`: Document adapter operations against fake coverage and real smoke status.

### Modified Capabilities

- `meeting-intelligence`: Add evidence grounding after schema validation.
- `workflows`: Store process provider/analyzer metadata and use it during approve.
- `lark-tools`: Clarify verification state for every adapter operation.
- `safety`: Extend write safety with provider binding and idempotency.
- `evaluation`: Split deterministic fixture metrics from optional real LLM extraction metrics.
- `product`: Make lifecycle MVP documentation truthful and internally consistent.

## Impact

- Affected code: `nanobot/meeting/evidence.py`, `schemas.py`, `analyzer.py`, `workflow.py`, `write_plan.py`, `cli.py`, `evals.py`, and meeting tests.
- Affected docs: `README.md`, `docs/PROJECT_BRIEF.md`, `docs/LIFECYCLE_DELIVERY_REPORT.md`, `docs/MVP_DELIVERY_REPORT.md`, `docs/BLOCKERS.md`, and new `docs/LARK_CLI_VERIFICATION_MATRIX.md`.
- No new external service is required.
- Real credentials remain local-only through environment variables, Keychain, and existing `lark-cli` auth state.
