# Proposal: Deliver Nanobot Meeting MVP

## Why

The bootstrap change established the nanobot architecture pivot. This change delivers the first working post-meeting MVP inside the HKUDS/nanobot v0.2.1 source tree.

The MVP needs to prove that Lark Meeting Agent is more than a transcript summarizer: it must read or ingest completed meeting content, extract evidence-linked outcomes, prepare collaboration writes safely, persist meeting memory, and answer historical questions with sources.

## What

Deliver a nanobot-based meeting extension with:

1. HKUDS/nanobot v0.2.1 source import while preserving existing Lark Meeting Agent docs and OpenSpec.
2. `nanobot/meeting/` domain workflow modules.
3. Pydantic v2 schemas for meetings, transcripts, evidence, minutes, write plans, runs, audit events, memory, and QA.
4. Transcript normalization from fixtures and Lark transcript/minutes text.
5. Deterministic `FakeMeetingAnalyzer` for CI and `OpenAICompatibleMeetingAnalyzer` for DeepSeek or another compatible LLM.
6. `LarkToolAdapter` with fake and `lark-cli` providers.
7. Dry-run `WritePlan` generation and approval-gated execution for Lark Docs, Tasks, and optional IM.
8. Workspace-local structured meeting memory and source-grounded QA.
9. Controlled nanobot `lark_meeting` tool and `lark-meeting` skill.
10. Fake tests, safety tests, optional real smoke paths, and real-mode run documentation.

## Non-goals

This change does not deliver:

1. pre-meeting brief workflow,
2. realtime meeting bot join,
3. custom ASR,
4. production OAuth onboarding,
5. complex frontend dashboard,
6. vector database optimization,
7. independent FastAPI app,
8. independent Feishu bot runtime,
9. independent generic agent runtime.

## Success Criteria

The change is successful when:

1. `openspec validate deliver-nanobot-meeting-mvp` passes.
2. `python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py` passes.
3. `pytest tests/meeting -q` passes without Lark or LLM credentials.
4. `ruff check nanobot tests` passes.
5. fake vertical slice runs end-to-end.
6. real-mode helper can verify local `lark-cli` auth and load the DeepSeek key from local Keychain without committing secrets.
7. writes remain approval-gated and route through `LarkToolAdapter`.
