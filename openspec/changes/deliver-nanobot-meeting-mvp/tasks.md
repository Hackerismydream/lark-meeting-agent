# Tasks: Deliver Nanobot Meeting MVP

## 1. OpenSpec Change

- [x] 1.1 Create `openspec/changes/deliver-nanobot-meeting-mvp/`.
- [x] 1.2 Add proposal, design, and tasks.
- [x] 1.3 Add delta specs for product, lark-tools, meeting-intelligence, workflows, memory, safety, entrypoints, and evaluation.

## 2. nanobot Import and Research

- [x] 2.1 Import HKUDS/nanobot v0.2.1 source into the repository root while preserving existing project docs/OpenSpec.
- [x] 2.2 Store upstream README/AGENTS/docs under `docs/`.
- [x] 2.3 Document import method in `docs/IMPLEMENTATION_NOTES.md`.
- [x] 2.4 Inspect extension points and document them in `docs/NANOBOT_EXTENSION_RESEARCH.md`.
- [x] 2.5 Choose least invasive integration surface: `nanobot/meeting/`, `nanobot/agent/tools/lark_meeting.py`, and `nanobot/skills/lark-meeting/SKILL.md`.

## 3. Fake CI Vertical Slice

- [x] 3.1 Add meeting Pydantic schemas.
- [x] 3.2 Add transcript normalizer.
- [x] 3.3 Add deterministic fake analyzer.
- [x] 3.4 Add write plan rendering.
- [x] 3.5 Add fake Lark provider.
- [x] 3.6 Add deterministic `PostMeetingWorkflow`.
- [x] 3.7 Add workspace-local meeting memory and QA.
- [x] 3.8 Add fixture transcript and fake Lark outputs.
- [x] 3.9 Add tests for schemas, normalizer, analyzer, adapter, workflow, memory, and tool route.

## 4. Real LLM and Real lark-cli

- [x] 4.1 Add OpenAI-compatible analyzer defaulting to DeepSeek environment variables.
- [x] 4.2 Validate LLM output with Pydantic schemas and one repair retry.
- [x] 4.3 Add `CliLarkProvider` for `auth.status`, `vc.search`, `vc.notes`, `docs.fetch`, `docs.create`, `task.create`, and `im.send`.
- [x] 4.4 Use argv arrays and `shell=False` for CLI invocation.
- [x] 4.5 Add `scripts/lma-real` to load DeepSeek key from local Keychain and verify `lark-cli` auth.
- [x] 4.6 Keep secrets out of repository files and docs.

## 5. Approval-gated Writes

- [x] 5.1 Generate write plans for docs/tasks/optional IM.
- [x] 5.2 Reject writes without approval in `LarkToolAdapter`.
- [x] 5.3 Execute only selected operation IDs on approve.
- [x] 5.4 Persist operation results and audit events.
- [x] 5.5 Mark unselected operations skipped.
- [x] 5.6 Keep `im.send` missing-target safe when no `chat_id` is supplied.

## 6. nanobot Entrypoint

- [x] 6.1 Add `LarkMeetingTool` with actions `process`, `approve`, `qa`, and `status`.
- [x] 6.2 Add JSON-schema-like tool parameter contract.
- [x] 6.3 Add `nanobot/skills/lark-meeting/SKILL.md`.
- [x] 6.4 Ensure tool calls deterministic workflow and never calls `lark-cli` directly.

## 7. Documentation and Review Artifacts

- [x] 7.1 Add `docs/MVP_REAL_DEMO.md`.
- [x] 7.2 Add `docs/IMPLEMENTATION_NOTES.md`.
- [x] 7.3 Add `docs/NANOBOT_EXTENSION_RESEARCH.md`.
- [x] 7.4 Add GPT Pro review prompt.
- [x] 7.5 Add real-mode helper usage to README.
- [x] 7.6 Add final `docs/MVP_DELIVERY_REPORT.md`.

## 8. Validation Gates

- [x] 8.1 Run `python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 8.2 Run `pytest tests/meeting -q`.
- [x] 8.3 Run `ruff check nanobot tests`.
- [x] 8.4 Run `openspec validate bootstrap-lark-meeting-agent`.
- [x] 8.5 Run `openspec validate deliver-nanobot-meeting-mvp`.
- [x] 8.6 Run fake CLI smoke test.
- [x] 8.7 Verify `scripts/lma-real status`.
- [x] 8.8 Scan staged/repo contents for committed DeepSeek/Lark secrets.

## 9. Remaining Manual Gates

- [ ] 9.1 Run a real Lark read + real LLM dry-run against a concrete meeting query. Blocked until user authorizes `vc:meeting.search:read` for lark-cli user identity.
- [ ] 9.2 Review WritePlan for a real run.
- [ ] 9.3 Execute approved real `docs.create`/`task.create` operations only after human review.
- [ ] 9.4 Optionally test `im.send` only with a safe explicit `chat_id`.
