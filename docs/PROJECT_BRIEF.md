# Lark Meeting Agent Project Brief

## 1. Project Name

Lark Meeting Agent

Chinese name: Feishu meeting workflow agent

## 2. One-line Description

Lark Meeting Agent is a Feishu/Lark-native lifecycle local MVP. It turns meeting transcripts and supplied meeting events into structured minutes, decisions, action items, risks, sourced briefs, and local meeting memory, then safely syncs approved outcomes to Lark docs, tasks, and IM messages.

## 3. Product Positioning

This product is not a generic chatbot and not a simple meeting summarizer.

It is a meeting workflow agent for enterprise collaboration. Its core value is to connect meeting understanding with collaboration execution and long-term memory.

The product helps users:

- prepare before meetings,
- understand meeting outcomes,
- generate structured minutes,
- sync action items,
- preserve project/customer/person memory,
- ask cross-meeting questions with source evidence.

## 4. Target Users

Primary users:

1. product managers,
2. project managers,
3. tech leads,
4. customer success managers,
5. sales engineers,
6. engineering managers,
7. new team members joining an existing project.

## 5. Product Problems

### Problem 1: No context before meetings

Users often enter meetings without knowing previous conclusions, unresolved issues, historical commitments, or customer concerns.

### Problem 2: Decisions and action items are lost during meetings

Meetings contain implicit decisions, verbal commitments, risks, and disagreements. These are often not captured in a reliable structure.

### Problem 3: No execution loop after meetings

Even when minutes exist, action items are not always converted into tasks or sent to the correct group.

### Problem 4: Cross-meeting knowledge is lost

Project and customer knowledge is scattered across meetings, docs, and chat history. It is difficult to answer questions such as "why did we make this decision?"

## 6. Product Journey

```text
Before meeting
  -> read calendar
  -> identify meeting type
  -> retrieve related history
  -> generate pre-brief

During meeting
  -> ingest transcript/event deltas
  -> maintain rolling summary
  -> detect decision/action candidates
  -> answer real-time questions

After meeting
  -> fetch or ingest transcript
  -> generate structured minutes
  -> extract decisions/action items/risks/open questions
  -> prepare Lark docs/tasks/IM write plan
  -> require approval
  -> execute approved writes
  -> persist meeting knowledge

Long-term
  -> project memory
  -> customer memory
  -> people memory
  -> cross-meeting QA with source evidence
```

## 7. Current Lifecycle Implementation

The current repository implements the lifecycle local MVP shape around the original post-meeting MVP. Post-meeting is the most complete closed-loop slice.

Implemented now:

- pre-meeting brief generation from agenda, related docs/tasks, historical meeting memory, entity memory, retrieval, and templates,
- live supplied transcript/event ingestion with rolling summary, decision/action/risk/question candidates, and source-grounded live QA,
- post-meeting transcript processing, structured minutes, evidence-linked decisions/action items, risks, open questions, write plans, and approval-gated writes,
- layered JSONL memory for meetings, transcript segments, minutes, decisions, action items, risks, open questions, entity memories, traces, and retrieval metadata,
- cross-meeting retrieval and QA with structured/keyword search plus an optional semantic retrieval interface,
- 31-case deterministic fixture regression benchmark with action/decision precision and recall, evidence coverage, schema success, safety, and QA source metrics.

Not implemented in this change:

- custom ASR,
- automatic bot join,
- unapproved realtime VC control,
- production OAuth onboarding,
- mandatory PostgreSQL/vector database service.

The lifecycle local MVP does not claim production meeting bot deployment, realtime ASR, or production Lark OAuth onboarding.

## 8. MVP

The original MVP only implemented the post-meeting workflow. The current implementation has moved beyond that into a lifecycle local MVP, while post-meeting remains the most complete closed-loop workflow.

MVP input:

- transcript fixture,
- or fake Lark provider meeting record.

MVP output:

- structured meeting minutes,
- decisions with evidence,
- action items with evidence,
- risks,
- open questions,
- dry-run Lark write plan,
- approval-gated fake execution,
- persisted meeting knowledge,
- simple cross-meeting QA with sources.

## 9. MVP Non-goals

The MVP does not include:

- custom ASR,
- realtime meeting bot,
- real Lark OAuth onboarding,
- complex frontend dashboard,
- arbitrary autonomous tool calling,
- production-grade multi-tenant permission system,
- vector database optimization,
- standalone FastAPI service as the core runtime,
- independent Feishu bot runtime,
- independent generic memory runtime,
- independent WebUI or model-routing runtime.

## 10. Nanobot Pivot

The project should be built from HKUDS/nanobot v0.2.1 rather than a standalone FastAPI app.

nanobot provides:

- agent loop and message bus,
- Feishu channel and other chat channels,
- WebUI,
- tools and tool discovery,
- skills,
- session and memory infrastructure,
- MCP,
- model/provider routing,
- deployment support,
- security and workspace policy.

Lark Meeting Agent adds:

- meeting-domain deterministic workflows,
- `LarkToolAdapter`,
- transcript normalization,
- structured extraction,
- evidence validation,
- write-plan approval,
- meeting structured memory,
- fixture-based evaluation.

## 11. Technical Principles

1. Reuse nanobot infrastructure where it already exists.
2. Deterministic workflow first, LLM second.
3. All external Lark operations go through `LarkToolAdapter`.
4. All LLM outputs are schema-validated.
5. Every decision and action item must preserve evidence.
6. Write operations require dry-run and approval.
7. Tests must run without real Lark credentials or real LLM keys.
8. Meeting content is untrusted input.
9. System behavior is specified through OpenSpec before code implementation.

## 12. Architecture Overview

```text
Feishu / WebUI / CLI / other nanobot channels
  -> nanobot MessageBus / AgentLoop / CommandRouter
      -> Lark Meeting entrypoint
      -> deterministic PreBriefWorkflow
          -> Read agenda/docs/tasks through LarkToolAdapter
          -> Retrieve history and open actions
          -> Generate sourced pre-brief
      -> deterministic LiveMeetingWorkflow
          -> Ingest transcript/event deltas
          -> Maintain rolling state
          -> Answer live QA with sources
      -> deterministic PostMeetingWorkflow
          -> ResolveMeeting
          -> FetchTranscript
          -> NormalizeTranscript
          -> AnalyzeMeeting
          -> BuildWritePlan
          -> RequestApproval
          -> ExecuteApprovedWrites
          -> PersistKnowledge
          -> ReturnResult
      -> Meeting Intelligence
      -> LarkToolAdapter
      -> Meeting Memory
  -> nanobot session/memory/provider/WebUI/deployment infrastructure
```

## 13. Core Workflow: PostMeetingWorkflow

```text
ResolveMeeting
  -> FetchTranscript
  -> NormalizeTranscript
  -> AnalyzeMeeting
  -> BuildWritePlan
  -> RequestApproval
  -> ExecuteApprovedWrites
  -> PersistKnowledge
  -> ReturnResult
```

nanobot AgentLoop may route user messages into the meeting entrypoint, but the workflow itself remains deterministic and testable.

## 14. Main Data Objects

- Meeting
- TranscriptSegment
- EvidenceRef
- MeetingMinutes
- Decision
- ActionItem
- Risk
- OpenQuestion
- WritePlan
- WriteOperation
- MeetingKnowledgeRecord
- MemoryCard
- Run
- PreBrief
- LiveMeetingState
- LiveMeetingEvent
- EntityMemory
- RetrievalResult
- RunTrace
- EvaluationReport

## 15. Delivery Phases

### Completed: Post-meeting MVP

- meeting domain module,
- controlled `lark_meeting` tool,
- `lark-meeting` skill instructions,
- transcript normalization,
- fake and LLM analyzer boundaries,
- evidence-linked minutes,
- write plan generation,
- approval-gated docs/tasks/IM writes,
- local JSONL meeting memory,
- source-grounded QA.

### Completed: Lifecycle Local MVP

- `PreBriefWorkflow` for read-only agenda/docs/tasks/memory context and templates,
- `LiveMeetingWorkflow` for supplied transcript/event deltas,
- `MemoryWorkflow` for layered records and entity memory,
- retrieval engine with structured filters and keyword scoring,
- run trace persistence and redaction,
- 31-case deterministic fixture regression benchmark.

### Current Hardening

- evidence integrity validation against transcript segments,
- provider-bound approval,
- write operation idempotency,
- Lark CLI verification matrix,
- optional LLM extraction benchmark contract,
- documentation truthfulness.

### Future Enhancements

- real readable Lark minutes/transcript gate once the authorized account has accessible data,
- LLM synthesis for pre-briefs,
- stronger live candidate consolidation,
- customer memory maturation,
- optional PostgreSQL/vector backend,
- production OAuth and deployment controls.
