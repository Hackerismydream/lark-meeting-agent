# Codex MVP Runbook

## Change

Use OpenSpec change:

```text
openspec/changes/deliver-nanobot-meeting-mvp/
```

The bootstrap change records the architecture pivot. The delivery change records the implemented MVP.

## Phase Loop

Each implementation phase should:

1. read relevant OpenSpec/docs,
2. implement only phase scope,
3. add or update tests,
4. run validation,
5. update `openspec/changes/deliver-nanobot-meeting-mvp/tasks.md`,
6. continue unless blocked.

## Phases

1. Import nanobot v0.2.1 and research extension points.
2. Implement fake vertical slice.
3. Implement real LLM analyzer.
4. Implement lark-cli read provider.
5. Implement WritePlan and approval-gated real writes.
6. Implement nanobot tool/skill integration.
7. Harden demo docs and delivery report.

## Validation

```bash
uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate deliver-nanobot-meeting-mvp
```

## Blocker Protocol

If blocked, write `docs/BLOCKERS.md` with:

- exact blocker,
- attempted fixes,
- remaining decision needed,
- safest next prompt.
