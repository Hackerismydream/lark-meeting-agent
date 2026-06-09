# Proposal: Bootstrap Lark Meeting Agent

## Why

Build the initial specification and project foundation for Lark Meeting Agent.

Lark Meeting Agent is a Feishu/Lark-native meeting workflow agent. Its long-term product goal is to support meeting preparation, meeting understanding, post-meeting execution, and cross-meeting memory.

The first implementation should focus on a narrow but complete post-meeting vertical slice. The goal is to avoid building a vague chatbot or a large unfinished SaaS. The MVP should demonstrate Agent engineering capability through deterministic workflows, safe tool execution, structured outputs, evidence preservation, and testability.

## Problem

Most meeting AI tools stop at transcription and summarization. In real enterprise collaboration, the deeper problems are:

1. users lack historical context before meetings,
2. meeting decisions and action items are often lost,
3. meeting minutes do not become executable tasks,
4. long-running projects lose the reasoning behind past decisions,
5. AI agents can create risk if they write to collaboration systems without approval.

This project should address these problems through workflow design, tool boundaries, and evidence-linked meeting intelligence.

## Scope

This change bootstraps the repository and defines the first system behavior for the MVP.

The MVP scope includes:

1. transcript fixture ingestion,
2. fake Lark provider support,
3. transcript normalization,
4. structured meeting minutes schema,
5. decision/action/risk/open-question extraction contract,
6. evidence references for decisions and action items,
7. Lark write plan contract for docs/tasks/IM,
8. dry-run and approval requirement for writes,
9. local knowledge persistence contract,
10. source-grounded cross-meeting QA contract.

## Non-goals

This change does not implement:

1. custom ASR,
2. real-time meeting bot,
3. production Lark OAuth onboarding,
4. complex frontend dashboard,
5. arbitrary autonomous tool calling,
6. production-grade multi-tenant security,
7. vector database optimization,
8. real Lark credentials in tests.

## Approach

Use OpenSpec to define system behavior before code.

The implementation should be split into later changes:

1. bootstrap project skeleton,
2. implement LarkToolAdapter,
3. implement MeetingAnalyzer,
4. implement PostMeetingWorkflow,
5. implement write plan rendering,
6. implement memory and QA,
7. implement pre-brief workflow,
8. optionally implement realtime meeting ingestion.

## Success Criteria

This change is successful when:

1. AGENTS.md defines repository development rules,
2. docs/PROJECT_BRIEF.md defines product and architecture,
3. OpenSpec delta specs define product, tools, intelligence, workflows, memory, safety, API, and evaluation requirements,
4. tasks.md defines an actionable implementation checklist,
5. the MVP is clearly constrained to post-meeting processing,
6. tests and fake providers are required by specification,
7. all risky Lark writes are approval-gated by specification.
