# Proposal: Bootstrap Lark Meeting Agent

## Why

Build the initial specification and project foundation for Lark Meeting Agent, now pivoted to a HKUDS/nanobot v0.2.1 based architecture.

Lark Meeting Agent is a Feishu/Lark-native meeting workflow agent. Its long-term product goal is to support meeting preparation, meeting understanding, post-meeting execution, and cross-meeting memory.

nanobot already provides a Python 3.11+ agent runtime with chat channels, Feishu channel, tools, memory, MCP, model routing, WebUI, deployment, and security/workspace controls. The project should not rebuild those capabilities as a standalone FastAPI application.

The first implementation should focus on a narrow but complete post-meeting vertical slice inside a nanobot fork/source checkout. The current change does not implement code; it aligns product contracts and OpenSpec with the nanobot pivot.

## Problem

Most meeting AI tools stop at transcription and summarization. In real enterprise collaboration, the deeper problems are:

1. users lack historical context before meetings,
2. meeting decisions and action items are often lost,
3. meeting minutes do not become executable tasks,
4. long-running projects lose the reasoning behind past decisions,
5. AI agents can create risk if they write to collaboration systems without approval.

This project should address these problems through deterministic workflow design, controlled nanobot tool/command entrypoints, LarkToolAdapter boundaries, and evidence-linked meeting intelligence.

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
9. local structured meeting knowledge persistence contract,
10. source-grounded cross-meeting QA contract,
11. nanobot-based entrypoint and extension-point research contract.

## Non-goals

This change does not implement:

1. application code,
2. nanobot source code,
3. custom ASR,
4. realtime meeting bot,
5. production Lark OAuth onboarding,
6. complex frontend dashboard,
7. arbitrary autonomous tool calling,
8. production-grade multi-tenant security,
9. vector database optimization,
10. real Lark credentials in tests,
11. standalone FastAPI service as the MVP core,
12. independent Feishu bot runtime,
13. independent generic memory runtime,
14. independent WebUI or model-routing runtime.

## Approach

Use OpenSpec to define system behavior before code.

The implementation should be split into later changes:

1. perform nanobot extension-point research,
2. update or confirm the OpenSpec after research,
3. create a minimal meeting-domain skeleton inside a nanobot fork/source checkout,
4. implement LarkToolAdapter,
5. implement transcript normalization and MeetingAnalyzer,
6. implement deterministic PostMeetingWorkflow,
7. implement write plan rendering and approval,
8. implement structured meeting memory and QA,
9. implement fixture-based evaluation,
10. later implement pre-brief workflow,
11. optionally implement realtime meeting ingestion.

## Success Criteria

This change is successful when:

1. AGENTS.md defines nanobot-based repository development rules,
2. docs/PROJECT_BRIEF.md defines product and nanobot-based architecture,
3. docs/ADR-001-adopt-nanobot-v0.2.1.md records the architecture decision,
4. OpenSpec delta specs define product, tools, intelligence, workflows, memory, safety, entrypoints, and evaluation requirements,
5. tasks.md defines an actionable nanobot-pivot implementation checklist,
6. the MVP is clearly constrained to post-meeting processing,
7. tests and fake providers are required by specification,
8. all risky Lark writes are approval-gated by specification,
9. OpenSpec validation passes,
10. no application code is added.
