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

- [ ] 4.1 Inspect nanobot v0.2.1 AgentLoop.
- [ ] 4.2 Inspect nanobot v0.2.1 CommandRouter.
- [ ] 4.3 Inspect nanobot v0.2.1 Tool and ToolLoader.
- [ ] 4.4 Inspect nanobot v0.2.1 Feishu channel.
- [ ] 4.5 Inspect nanobot v0.2.1 skills.
- [ ] 4.6 Inspect nanobot v0.2.1 memory/session model.
- [ ] 4.7 Inspect nanobot v0.2.1 security/workspace settings.
- [ ] 4.8 Inspect nanobot v0.2.1 Python SDK and OpenAI-compatible API.
- [ ] 4.9 Inspect nanobot v0.2.1 WebUI/gateway.
- [ ] 4.10 Update OpenSpec if research changes the preferred extension point.

## 5. Later Implementation Skeleton Inside nanobot Fork

- [ ] 5.1 Fork or source-checkout HKUDS/nanobot v0.2.1.
- [ ] 5.2 Carry the reviewed OpenSpec/docs/ADR into the nanobot-based worktree.
- [ ] 5.3 Add meeting-domain module shape under `nanobot/meeting/`.
- [ ] 5.4 Add controlled tool or command entrypoint.
- [ ] 5.5 Add `nanobot/skills/lark-meeting/SKILL.md`.
- [ ] 5.6 Add `tests/meeting/` and `tests/fixtures/meeting/`.

## 6. Later Meeting Schema and Analyzer

- [ ] 6.1 Add meeting schemas.
- [ ] 6.2 Add transcript normalization.
- [ ] 6.3 Add fake analyzer.
- [ ] 6.4 Add optional LLM analyzer boundary.
- [ ] 6.5 Add evidence validation.
- [ ] 6.6 Add malformed transcript tests.
- [ ] 6.7 Add analyzer output without evidence tests.

## 7. Later Fake Provider and Deterministic Workflow

- [ ] 7.1 Add fake Lark provider.
- [ ] 7.2 Add deterministic PostMeetingWorkflow.
- [ ] 7.3 Add successful post-meeting dry-run flow.
- [ ] 7.4 Add missing transcript handling.
- [ ] 7.5 Add user rejects writes flow.
- [ ] 7.6 Add selected write operations approved flow.

## 8. Later LarkToolAdapter Write-plan Approval

- [ ] 8.1 Add LarkToolAdapter allowlist.
- [ ] 8.2 Block direct `lark-cli` through nanobot exec.
- [ ] 8.3 Add dry-run WritePlan generation.
- [ ] 8.4 Add approval-gated write execution.
- [ ] 8.5 Add malformed tool output handling.
- [ ] 8.6 Add tool-call audit events.

## 9. Later Fixture-based Evaluation

- [ ] 9.1 Add transcript fixtures.
- [ ] 9.2 Add expected extraction fixtures.
- [ ] 9.3 Add fake analyzer evaluation.
- [ ] 9.4 Add evidence coverage metric.
- [ ] 9.5 Add source-grounded QA tests.

## Rejected Old Plan

- [ ] Do not create a standalone `app/` directory as the MVP core.
- [ ] Do not add FastAPI as the MVP core framework.
- [ ] Do not add SQLAlchemy/PostgreSQL as bootstrap requirements.
- [ ] Do not implement `GET /health` as the first product milestone.
- [ ] Do not treat `/api/meetings/process` as the MVP primary entrypoint.
- [ ] Do not run `mypy app` unless a later nanobot-compatible type-checking plan requires it.
