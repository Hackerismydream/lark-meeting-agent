## Why

The current system proves a post-meeting MVP, but the target product and resume story require a fuller meeting workflow agent: pre-meeting context preparation, live meeting understanding from incremental transcript/events, post-meeting writeback, long-term memory, source-grounded QA, and measurable safety/evaluation gates.

This change turns the existing post-meeting slice into a lifecycle meeting agent while preserving the current safety posture: deterministic workflows, controlled Lark tooling, schema-validated LLM output, evidence requirements, and approval-gated writes.

## What Changes

- Add `PreBriefWorkflow` to prepare meeting context from calendar agenda, historical meeting memory, open action items, related documents, and entity memory.
- Add `LiveMeetingWorkflow` to consume incremental transcript/event input, maintain rolling meeting state, extract candidate decisions/actions/risks/questions, and answer in-meeting questions with timestamped evidence.
- Extend `PostMeetingWorkflow` instead of replacing it, keeping process/approve behavior and evidence-linked structured minutes.
- Extend `MemoryWorkflow` and storage to support meeting knowledge objects, memory cards, open action items, entity memories, run traces, and optional vector/semantic retrieval.
- Extend `LarkToolAdapter` with additional read operations needed for lifecycle workflows while retaining allowlist, read/write separation, dry-run, approval, timeout, retry, audit, and redaction behavior.
- Add RAG-style retrieval over local meeting memory using structured filters, keyword search, and optional semantic vector search.
- Add benchmark fixtures and evaluation scripts for normalization, extraction precision/recall, evidence coverage, tool safety, and QA citation accuracy.
- Update the nanobot `lark_meeting` tool and skill to expose lifecycle actions without granting arbitrary Lark tool access.

## Capabilities

### New Capabilities

- `prebrief-workflow`: Pre-meeting brief generation from calendar, prior meetings, open action items, docs, and long-term entity memory.
- `live-meeting-workflow`: In-meeting incremental understanding and source-grounded live QA over transcript/event streams.
- `rag-retrieval`: Cross-meeting retrieval using structured filters, keyword search, and optional semantic vectors.
- `meeting-evaluation`: Reproducible benchmark and regression metrics for extraction, evidence, tools, and QA.
- `run-trace`: Persisted workflow traces for debugging, audit, and resume-ready evidence.

### Modified Capabilities

- `product`: Reposition the product contract from post-meeting MVP to lifecycle meeting agent while keeping explicit non-goals for custom ASR and automatic bot join.
- `workflows`: Add pre-brief, live, memory, and evaluation workflows around the existing post-meeting workflow.
- `lark-tools`: Extend the adapter allowlist and provider contract for calendar agenda, task queries, doc reads, and retry behavior.
- `meeting-intelligence`: Add pre-brief schemas, live rolling state, candidate extraction, entity memory, and stricter metrics for action/decision extraction.
- `memory`: Add structured entity memories, open action item indexes, retrieval metadata, and optional vector index support.
- `entrypoints`: Extend the nanobot tool action surface for lifecycle workflows.
- `safety`: Extend safety gates for live transcript injection, write approval tokens, trace redaction, and malformed tool output.
- `evaluation`: Add measurable benchmarks and acceptance thresholds aligned to the lifecycle resume claims.

## Impact

- Affected code: `nanobot/meeting/`, `nanobot/agent/tools/lark_meeting.py`, `nanobot/skills/lark-meeting/SKILL.md`, `tests/meeting/`, `tests/fixtures/meeting/`, and lifecycle validation scripts under `scripts/`.
- Affected data: workspace-local `.lark_meeting_agent/` memory layout gains trace, entity-memory, open-action, retrieval, and benchmark artifacts. Existing MVP JSONL files remain readable.
- Affected integrations: DeepSeek/OpenAI-compatible analyzer remains optional for real runs; fake analyzers and fake Lark providers remain mandatory for CI.
- Affected Lark operations: adapter adds read-side operations for agenda, task lookup, document fetch/search, and meeting metadata. Write operations remain approval-gated and limited to docs, tasks, and IM unless a later change explicitly expands them.
- Dependencies: no heavy service is required for the first lifecycle implementation. PostgreSQL and vector search are optional backends behind interfaces; JSONL and local retrieval remain the default implementation.
