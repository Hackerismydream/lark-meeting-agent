## Context

The repository currently contains a working post-meeting MVP:

- `PostMeetingWorkflow` processes transcript files or readable Lark meeting notes.
- `TranscriptNormalizer -> MeetingAnalyzer -> MeetingMinutes` produces evidence-linked structured outputs.
- `LarkToolAdapter` is the only Lark boundary and write operations require approval.
- `.lark_meeting_agent/` stores JSONL meeting memory, run snapshots, and audit events.
- `lark_meeting` exposes process, approve, qa, and status actions.

The lifecycle target extends this shape rather than replacing it. The existing code remains the post-meeting spine; new workflows reuse the same schemas, adapter, analyzer boundary, memory store, and nanobot tool surface.

## Goals / Non-Goals

**Goals:**

- Deliver a lifecycle meeting agent with pre-meeting, live-meeting, post-meeting, memory, retrieval, safety, and evaluation capabilities.
- Keep all Lark access behind `LarkToolAdapter`.
- Keep write operations dry-run plus approval by default.
- Make all resume metrics reproducible from fixtures, benchmark scripts, and persisted run traces.
- Support real DeepSeek/lark-cli paths without requiring real credentials in CI.
- Support JSONL/local retrieval as the default backend and keep PostgreSQL/vector search behind optional interfaces.

**Non-Goals:**

- No custom ASR implementation.
- No automatic bot join or realtime VC bot control in this change.
- No production OAuth onboarding.
- No independent FastAPI service or separate Feishu bot runtime.
- No mandatory PostgreSQL, Milvus, Qdrant, Celery, React dashboard, or other heavy service dependency.
- No autonomous free-form Lark tool calling.

## Decisions

### Decision: Add lifecycle workflows around the current post-meeting spine

Add four deterministic workflows under `nanobot/meeting/`:

```text
PreBriefWorkflow
  -> calendar/task/doc/meeting reads via LarkToolAdapter
  -> MeetingMemoryStore / RetrievalEngine
  -> PreBrief

LiveMeetingWorkflow
  -> incremental transcript/event input
  -> TranscriptNormalizer
  -> LiveMeetingState / LiveMeetingAnswer
  -> candidate decisions/actions/risks/questions

PostMeetingWorkflow
  -> existing process/approve behavior
  -> minor extension for richer knowledge objects

MemoryWorkflow
  -> meeting/minutes/action/entity memory cards
  -> retrieval index refresh
  -> source-grounded QA
```

This is preferred over a single monolithic `MeetingAgent` because each stage has different inputs, safety risks, and acceptance tests. The nanobot tool remains thin and routes to deterministic workflows.

Alternative considered: let an LLM plan arbitrary tool calls. That is rejected for this repository because Lark writes have enterprise side effects and must remain approval-gated.

### Decision: Treat live meeting as event-stream understanding, not bot join

`LiveMeetingWorkflow` consumes transcript deltas and meeting events supplied by fixtures, local streams, or later channel adapters. It maintains rolling state and answers live questions with sources.

This satisfies in-meeting understanding without depending on automatic bot join, realtime VC control, or custom transcription. A later change can add `lark-vc-agent` ingestion behind the same event interface if permissions and safety are ready.

Alternative considered: implement automatic meeting bot join now. That is rejected because it introduces new identity, permission, recording consent, and realtime reliability risks that are not necessary for the resume-ready engineering claim.

### Decision: Use JSONL/local retrieval first, optional vector backend second

Default persistence stays under `.lark_meeting_agent/` with JSONL, snapshots, and trace files. Retrieval starts with structured filters plus keyword scoring. Optional vector search is exposed through an interface and local deterministic embeddings for tests; production embedding/vector providers are not required for CI.

This keeps the project runnable locally and makes benchmark evidence reproducible. PostgreSQL/vector search can be added behind the same repository interfaces after the JSONL baseline is proven.

Alternative considered: move directly to PostgreSQL plus vector DB. That is rejected for this change because it would add operational weight before the workflow contracts are stable.

### Decision: Extend adapter allowlist by operation class, not by provider escape hatches

`LarkToolAdapter` gains read operations required for lifecycle workflows, including calendar agenda, task search/list, document search/fetch, meeting search/notes, and minutes search. Writes remain limited to docs, tasks, and IM unless a later spec expands the write set.

The provider contract gets retries and timeouts, but workflows still receive typed results and audit events. No workflow or analyzer calls `lark-cli`, HTTP APIs, SDKs, or shell tools directly.

Alternative considered: reuse nanobot's general shell/exec tool for Lark calls. That remains rejected because it bypasses the adapter audit and approval model.

### Decision: Make evaluation fixtures the source of metrics

The resume claims require evidence. Add benchmark fixtures with expected decisions, action items, evidence refs, and QA answers. Evaluation scripts compute:

- action item precision/recall,
- decision precision/recall,
- evidence coverage,
- schema validation success rate,
- tool call success rate,
- QA source accuracy,
- safety regression pass rate.

The first implementation may use 30+ compact synthetic and sanitized fixtures rather than private real meetings. Real Lark smoke remains optional and documented separately.

## Risks / Trade-offs

- [Risk] The lifecycle scope can grow beyond a reviewable unit. -> Mitigation: implement in commits by artifact, schemas, adapter, pre-brief, live, memory/retrieval, evaluation, docs.
- [Risk] Local keyword retrieval may not satisfy all RAG expectations. -> Mitigation: expose a retrieval interface and report keyword/local semantic metrics separately.
- [Risk] LLM normalization can over-tolerate malformed output. -> Mitigation: keep Pydantic validation strict for final objects and count repair/normalization in evaluation output.
- [Risk] Real Lark data may remain unavailable for current account. -> Mitigation: CI uses fake providers; real smoke reports distinguish "code path works" from "account has readable minutes".
- [Risk] Live transcript input can contain prompt injection. -> Mitigation: treat all transcript/doc/message content as untrusted, reject embedded tool instructions, and add safety fixtures.
- [Risk] Entity memory can imply unsupported facts across meetings. -> Mitigation: memory cards retain source meeting IDs and QA answers must cite source segments.

## Migration Plan

1. Add lifecycle OpenSpec artifacts and validate the change.
2. Add schema/model extensions without changing existing post-meeting behavior.
3. Extend `LarkToolAdapter` fake/CLI providers and tests.
4. Implement pre-brief workflow and fixtures.
5. Implement live workflow and fixtures.
6. Implement memory/retrieval extensions and source-grounded QA improvements.
7. Add evaluation fixtures/scripts and benchmark documentation.
8. Extend nanobot tool actions and skill instructions.
9. Update README/project docs and run validation gates.

Rollback is straightforward before real writes because new data is additive under `.lark_meeting_agent/`. Existing post-meeting snapshots stay readable. If a lifecycle workflow fails, the tool can keep routing only to current process/approve/qa/status actions.

## Open Questions

- Real Lark readable minutes remain account-dependent. This does not block lifecycle implementation because fake fixtures and lark-cli smoke paths cover code behavior.
- PostgreSQL backend is intentionally optional for this change. JSONL remains the default until the workflow and retrieval metrics prove the need for a service backend.
