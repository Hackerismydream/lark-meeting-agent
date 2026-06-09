# Lark Meeting Agent Project Brief

## 1. Project Name

Lark Meeting Agent

中文名：飞书会议全流程智能体

## 2. One-line Description

Lark Meeting Agent is a Feishu/Lark-native meeting workflow agent that turns meeting transcripts into structured minutes, decisions, action items, risks, and long-term project memory, then safely syncs approved outcomes to Lark docs, tasks, and IM messages.

## 3. Product Positioning

This product is not a generic chatbot and not a simple meeting summarizer.

It is a workflow agent for enterprise collaboration. Its core value is to connect meeting understanding with collaboration execution and long-term memory.

The product helps users:

- prepare before meetings,
- understand meeting outcomes,
- generate structured minutes,
- sync action items,
- preserve project/customer/person memory,
- ask cross-meeting questions with source evidence.

## 4. Target Users

Primary users:

1. Product managers
2. Project managers
3. Tech leads
4. Customer success managers
5. Sales engineers
6. Engineering managers
7. New team members joining an existing project

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
- real-time meeting bot,
- real Lark OAuth onboarding,
- complex frontend dashboard,
- arbitrary autonomous tool calling,
- production-grade multi-tenant permission system,
- vector database optimization.

## 9. Technical Principles

1. Deterministic workflow first, LLM second.
2. All external Lark operations go through `LarkToolAdapter`.
3. All LLM outputs are schema-validated.
4. Every decision and action item must preserve evidence.
5. Write operations require dry-run and approval.
6. Tests must run without real Lark credentials.
7. Meeting content is untrusted input.
8. System behavior is specified through OpenSpec before code implementation.

## 10. Architecture Overview

```text
User / Lark Bot / API
  -> API Layer
  -> Workflow Layer
      -> PostMeetingWorkflow
      -> PreBriefWorkflow
      -> CrossMeetingQAWorkflow
  -> Intelligence Layer
      -> TranscriptNormalizer
      -> MeetingAnalyzer
      -> WritePlanBuilder
      -> RetrievalService
      -> MemoryService
  -> Tool Layer
      -> LarkToolAdapter
      -> FakeLarkProvider
      -> CliLarkProvider
  -> Storage Layer
      -> Local DB / Postgres later
      -> Fixtures for tests
```

## 11. Core Workflow: PostMeetingWorkflow

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

## 12. Main Data Objects

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
- MemoryCard
- Run

## 13. Development Roadmap

### Phase 1: Bootstrap

- Python project skeleton
- FastAPI health check
- config and logging
- core Pydantic schemas
- tests, ruff, mypy

### Phase 2: LarkToolAdapter

- fake provider
- CLI provider shell boundary
- allowlist
- dry-run
- approval
- audit logs

### Phase 3: MeetingAnalyzer

- transcript normalization
- structured minutes
- decisions/action items/risks/open questions
- evidence validation
- fake analyzer and LLM interface

### Phase 4: PostMeetingWorkflow

- explicit workflow state machine
- process endpoint
- approval endpoint
- fake write execution

### Phase 5: Memory and QA

- persistence
- retrieval interface
- source-grounded QA

### Phase 6: Pre-brief

- calendar agenda
- meeting type classification
- related history retrieval
- unresolved action item retrieval

### Phase 7: Optional realtime

- event schema
- fake transcript deltas
- rolling summary
- current meeting state
