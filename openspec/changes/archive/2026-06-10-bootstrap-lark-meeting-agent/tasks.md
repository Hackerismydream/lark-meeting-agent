# Tasks: Bootstrap Lark Meeting Agent

> Phase gate: do not implement nanobot meeting code until this nanobot pivot OpenSpec has been reviewed and approved.

## 1. Documentation and OpenSpec Pivot

- [x] 1.1 Update `AGENTS.md` to adopt HKUDS/nanobot v0.2.1 as the target runtime.
- [x] 1.2 Update `README.md` with OpenSpec bootstrap status and validation commands.
- [x] 1.3 Update `docs/PROJECT_BRIEF.md` from standalone FastAPI app to nanobot-based meeting extension.
- [x] 1.4 Add `docs/ADR-001-adopt-nanobot-v0.2.1.md`.
- [x] 1.5 Update `docs/GPT_PRO_REVIEW_PROMPT.txt` for nanobot pivot review.

## 2. OpenSpec Delta Pivot

- [x] 2.1 Update product delta spec.
- [x] 2.2 Update lark-tools delta spec.
- [x] 2.3 Update meeting-intelligence delta spec.
- [x] 2.4 Update workflows delta spec.
- [x] 2.5 Update memory delta spec.
- [x] 2.6 Update safety delta spec.
- [x] 2.7 Reframe API spec as entrypoint contract.
- [x] 2.8 Update evaluation delta spec.

## 3. OpenSpec Validation

- [x] 3.1 Run `openspec validate bootstrap-lark-meeting-agent`.
- [x] 3.2 Check `git diff --stat`.
- [x] 3.3 Confirm no application code was added.
- [x] 3.4 Confirm no forbidden paths were created: `app/`, `tests/`, `pyproject.toml`, `nanobot/`, `webui/`, `Dockerfile`, migrations, real Lark integration code, or real LLM provider code.

## 4. nanobot Extension-point Research

- [x] 4.1 Inspect nanobot v0.2.1 AgentLoop.
- [x] 4.2 Inspect nanobot v0.2.1 CommandRouter.
- [x] 4.3 Inspect nanobot v0.2.1 Tool and ToolLoader.
- [x] 4.4 Inspect nanobot v0.2.1 Feishu channel.
- [x] 4.5 Inspect nanobot v0.2.1 skills.
- [x] 4.6 Inspect nanobot v0.2.1 memory/session model.
- [x] 4.7 Inspect nanobot v0.2.1 security/workspace settings.
- [x] 4.8 Inspect nanobot v0.2.1 Python SDK and OpenAI-compatible API.
- [x] 4.9 Inspect nanobot v0.2.1 WebUI/gateway.
- [x] 4.10 Update OpenSpec if research changes the preferred extension point.

## 5. Later Implementation Skeleton Inside nanobot Fork

- [x] 5.1 Fork or source-checkout HKUDS/nanobot v0.2.1.
- [x] 5.2 Carry the reviewed OpenSpec/docs/ADR into the nanobot-based worktree.
- [x] 5.3 Add meeting-domain module shape under `nanobot/meeting/`.
- [x] 5.4 Add controlled tool or command entrypoint.
- [x] 5.5 Add `nanobot/skills/lark-meeting/SKILL.md`.
- [x] 5.6 Add `tests/meeting/` and `tests/fixtures/meeting/`.

## 6. Later Meeting Schema and Analyzer

- [x] 6.1 Add meeting schemas.
- [x] 6.2 Add transcript normalization.
- [x] 6.3 Add fake analyzer.
- [x] 6.4 Add optional LLM analyzer boundary.
- [x] 6.5 Add evidence validation.
- [x] 6.6 Add malformed transcript tests.
- [x] 6.7 Add analyzer output without evidence tests.

## 7. Later Fake Provider and Deterministic Workflow

- [x] 7.1 Add fake Lark provider.
- [x] 7.2 Add deterministic PostMeetingWorkflow.
- [x] 7.3 Add successful post-meeting dry-run flow.
- [x] 7.4 Add missing transcript handling.
- [x] 7.5 Add user rejects writes flow.
- [x] 7.6 Add selected write operations approved flow.

## 8. Later LarkToolAdapter Write-plan Approval

- [x] 8.1 Add LarkToolAdapter allowlist.
- [x] 8.2 Block direct `lark-cli` through nanobot exec.
- [x] 8.3 Add dry-run WritePlan generation.
- [x] 8.4 Add approval-gated write execution.
- [x] 8.5 Add malformed tool output handling.
- [x] 8.6 Add tool-call audit events.

## 9. Later Fixture-based Evaluation

- [x] 9.1 Add transcript fixtures.
- [x] 9.2 Add expected extraction fixtures.
- [x] 9.3 Add fake analyzer evaluation.
- [x] 9.4 Add evidence coverage metric.
- [x] 9.5 Add source-grounded QA tests.

## Rejected Old Plan

- [x] Do not create a standalone `app/` directory as the MVP core.
- [x] Do not add FastAPI as the MVP core framework.
- [x] Do not add SQLAlchemy/PostgreSQL as bootstrap requirements.
- [x] Do not implement `GET /health` as the first product milestone.
- [x] Do not treat `/api/meetings/process` as the MVP primary entrypoint.
- [x] Do not run `mypy app` unless a later nanobot-compatible type-checking plan requires it.
