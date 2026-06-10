## Context

Current `main` implements a lifecycle local MVP. GPT review identified the right next move: stop adding broad features and harden the implementation so claims are defensible.

The current gaps are specific:

- `Decision` and `ActionItem` require `evidence_refs`, but segment IDs and quotes are not strictly checked against normalized transcript segments.
- `approve` uses the workflow instance provider mode, which can diverge from the provider used during `process`.
- Repeated `approve` can execute completed operations again.
- Evaluation reports 31-case fixture metrics but the naming can be misread as real LLM or production performance.
- Docs still contain mixed post-meeting MVP and lifecycle MVP language.

## Goals / Non-Goals

**Goals:**

- Ground evidence refs against normalized transcript segments.
- Store provider/analyzer metadata in run snapshots.
- Use stored provider mode for approval by default.
- Reject provider mismatches unless explicit override is requested.
- Add idempotency keys and skip already completed operations.
- Split deterministic fixture regression from optional LLM extraction benchmark.
- Add honest Lark CLI verification matrix and fix docs consistency.

**Non-Goals:**

- No custom ASR.
- No automatic meeting bot join.
- No production OAuth.
- No PostgreSQL/vector DB implementation.
- No new frontend.
- No new Lark write operation type.
- No unapproved real Lark writes.

## Decisions

### Decision: Evidence integrity is a second validation layer

Pydantic schemas remain responsible for structure. `EvidenceIntegrityValidator` is responsible for grounding: every evidence segment must exist; mismatched quotes are replaced with exact segment text so model-invented quotes are not preserved; unknown segment IDs raise `EvidenceValidationError`.

### Decision: Approval uses run snapshot provider by default

`Run` stores `provider_mode` and `analyzer_mode`. `approve` uses `run.provider_mode` unless the caller explicitly requests an override. CLI exposes override as a separate flag so default behavior cannot silently switch a real run to fake or the reverse.

### Decision: Idempotency is tracked per write operation

Each `WriteOperation` gets a stable `idempotency_key`. A completed operation is not executed again on repeated approve; the previous result is kept and the operation is left completed.

### Decision: Evaluation names must match evidence strength

The existing 31-case benchmark becomes `deterministic-regression`. Optional real LLM extraction runs only with `RUN_REAL_LLM_TESTS=1` and must not be claimed unless actually executed.

## Risks / Trade-offs

- [Risk] Quote backfill can hide a poor LLM quote. -> Mitigation: backfill prevents fabricated quote persistence and tests assert the behavior.
- [Risk] Provider binding changes approval behavior. -> Mitigation: add regression tests for fake process/approve, CLI snapshot metadata, mismatch rejection, override, and repeated approve.
- [Risk] Docs become too conservative. -> Mitigation: keep lifecycle local MVP claims, but mark real Lark and production limitations explicitly.

## Migration Plan

Existing run snapshots omit new fields. Defaults keep them loadable: provider defaults to fake, analyzer defaults to fake, idempotency keys are optional/backfilled for newly built write plans.
