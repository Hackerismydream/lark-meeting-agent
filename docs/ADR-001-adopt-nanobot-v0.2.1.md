# ADR-001: Adopt HKUDS/nanobot v0.2.1

## Status

Accepted for OpenSpec bootstrap.

## Context

Lark Meeting Agent needs chat delivery, agent runtime, tool execution, model routing, memory, Feishu integration, WebUI, deployment, and safety controls.

HKUDS/nanobot v0.2.1 already provides these runtime capabilities as a Python 3.11+ lightweight agent stack. Rebuilding them in a standalone FastAPI application would duplicate the base platform before the meeting-domain problem is solved.

## Decision

Lark Meeting Agent will be specified as a HKUDS/nanobot v0.2.1 fork or source-based extension.

The bootstrap phase remains documentation and OpenSpec only. It does not clone, vendor, or copy nanobot source into this repository.

## Reused nanobot Capabilities

- AgentLoop and MessageBus
- CommandRouter
- Feishu channel
- WebUI and gateway
- tools and ToolLoader
- skills
- session and memory infrastructure
- provider/model routing
- MCP support
- deployment support
- security/workspace policy

## Capabilities Implemented by Lark Meeting Agent

- meeting-domain schemas,
- deterministic PostMeetingWorkflow,
- transcript normalization,
- MeetingAnalyzer with fake and optional LLM implementations,
- evidence validation,
- LarkToolAdapter,
- dry-run WritePlan generation,
- approval-gated write execution,
- structured meeting memory,
- source-grounded cross-meeting QA,
- fixture-based evaluation.

## Conceptual Location of PostMeetingWorkflow

PostMeetingWorkflow should live in a meeting-domain module inside the future nanobot fork/source checkout. nanobot may route messages, commands, or tool calls to it, but the workflow itself remains deterministic and testable.

The intended later shape is:

```text
nanobot/meeting/
nanobot/agent/tools/lark_meeting.py
nanobot/skills/lark-meeting/SKILL.md
tests/meeting/
tests/fixtures/meeting/
```

## LarkToolAdapter Boundary

All Lark operations still go through `LarkToolAdapter`.

This remains true even though nanobot has general tools and optional shell execution. The meeting workflow must not call `lark-cli`, Lark HTTP APIs, Lark SDKs, or nanobot's general exec tool directly.

## MVP Scope

The MVP remains post-meeting only.

Out of scope:

- realtime meeting bot,
- automatic bot join,
- custom ASR,
- production OAuth onboarding,
- vector database optimization,
- complex frontend dashboard,
- standalone FastAPI service as the core runtime.

## Consequences

The project must first research nanobot extension points before implementation. OpenSpec tasks should not start with `app/`, FastAPI, SQLAlchemy, or standalone REST endpoints.

The implementation should focus on meeting-domain value while reusing nanobot's existing runtime surface.
