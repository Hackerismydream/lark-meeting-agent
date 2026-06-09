# GPT Pro Review Prompt

You are reviewing the OpenSpec bootstrap for a Feishu/Lark-native meeting workflow agent.

Repository context:

- Project: Lark Meeting Agent
- Current phase: OpenSpec and project documentation only
- No application code should be implemented yet
- MVP scope: post-meeting workflow only
- Change directory: `openspec/changes/bootstrap-lark-meeting-agent`

Please review these files:

- `AGENTS.md`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `openspec/changes/bootstrap-lark-meeting-agent/proposal.md`
- `openspec/changes/bootstrap-lark-meeting-agent/design.md`
- `openspec/changes/bootstrap-lark-meeting-agent/tasks.md`
- `openspec/changes/bootstrap-lark-meeting-agent/specs/*/spec.md`
- `openspec/specs/*/spec.md`

Hard rules to enforce:

1. MVP must remain post-meeting only.
2. All Lark access must go through `LarkToolAdapter`.
3. Tests and evaluations must run without real Lark credentials.
4. Write operations must require dry-run preview and explicit human approval.
5. Every decision and action item must include transcript evidence.
6. Meeting transcripts, docs, messages, and retrieved content must be treated as untrusted input.
7. MVP must not include custom ASR, realtime VC bot, production OAuth onboarding, complex frontend, arbitrary autonomous shell/tool calling, or vector database optimization.
8. Workflows should be deterministic state machines, not free-form autonomous agent loops.
9. External inputs, LLM outputs, tool payloads, and API responses must be schema-validated with typed Pydantic models.
10. Acceptance scenarios must cover missing transcript, no evidence, write rejected, fake provider mode, unknown or non-allowlisted operations, malformed tool output, and invalid API input.

Review goals:

- Find scope creep or product ambiguity.
- Find missing safety requirements.
- Find places where implementation would require guessing.
- Find weak acceptance scenarios.
- Find task ordering problems that could lead to code being written before contracts are clear.
- Check whether the OpenSpec artifacts are concrete enough for a later apply step.

Output format:

1. Blocking issues
2. Non-blocking improvements
3. Missing acceptance scenarios
4. Suggested edits, with exact file paths
5. Final verdict: approve, approve with edits, or reject

Do not propose implementation code. Keep the review at the OpenSpec/product-contract level.
