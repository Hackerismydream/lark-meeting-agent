# Lark Meeting Agent Project Brief

## 1. Project Name

Lark Meeting Agent

Chinese name: Feishu meeting workflow agent

## 2. One-line Description

Lark Meeting Agent is a Feishu/Lark-native meeting workflow agent built as a HKUDS/nanobot v0.2.1 extension. It turns meeting transcripts into structured minutes, decisions, action items, risks, and long-term project memory, then safely syncs approved outcomes to Lark docs, tasks, and IM messages.

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

## 7. MVP

The MVP only implements the post-meeting workflow.

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

## 8. MVP Non-goals

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

## 9. Nanobot Pivot

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

## 10. Technical Principles

1. Reuse nanobot infrastructure where it already exists.
2. Deterministic workflow first, LLM second.
3. All external Lark operations go through `LarkToolAdapter`.
4. All LLM outputs are schema-validated.
5. Every decision and action item must preserve evidence.
6. Write operations require dry-run and approval.
7. Tests must run without real Lark credentials or real LLM keys.
8. Meeting content is untrusted input.
9. System behavior is specified through OpenSpec before code implementation.

## 11. Architecture Overview

```text
Feishu / WebUI / CLI / other nanobot channels
  -> nanobot MessageBus / AgentLoop / CommandRouter
  -> Lark Meeting entrypoint
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

## 12. Core Workflow: PostMeetingWorkflow

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

## 13. Main Data Objects

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

## 14. Development Roadmap

### Phase 1: Documentation and OpenSpec Pivot

- update product documents,
- update OpenSpec artifacts,
- add ADR for nanobot adoption,
- validate with OpenSpec.

### Phase 2: nanobot Extension-point Research

- inspect AgentLoop,
- inspect CommandRouter,
- inspect Tool and ToolLoader,
- inspect Feishu channel,
- inspect skills,
- inspect memory,
- inspect security/workspace policy,
- inspect Python SDK,
- inspect OpenAI-compatible API,
- inspect WebUI/gateway.

### Phase 3: Later Implementation Skeleton Inside nanobot Fork

- add meeting domain module,
- add controlled meeting tool or command,
- add skill instructions,
- add fixture directories.

### Phase 4: Meeting Schema and Analyzer

- define schemas,
- implement normalizer,
- implement fake analyzer,
- define optional LLM analyzer boundary,
- enforce evidence validation.

### Phase 5: PostMeetingWorkflow

- implement deterministic state machine,
- connect fake provider,
- build write plan,
- preserve run state.

### Phase 6: LarkToolAdapter Write-plan Approval

- enforce allowlist,
- enforce dry-run,
- support approval,
- record audit events.

### Phase 7: Memory, QA, and Evaluation

- persist structured meeting knowledge,
- support source-grounded QA,
- run fixture-based evaluations.

### Future: Pre-brief and Realtime

- pre-brief workflow,
- realtime transcript/event deltas,
- live meeting support.
