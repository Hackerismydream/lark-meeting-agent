# MVP Acceptance Gates

## Gate 1: Repository Shape

Must contain:

```text
nanobot/
pyproject.toml
docs/
openspec/
nanobot/meeting/
nanobot/agent/tools/lark_meeting.py
nanobot/skills/lark-meeting/SKILL.md
tests/meeting/
scripts/lma-real
```

Must not contain committed secrets, standalone FastAPI MVP core, custom ASR, or unreviewed vector DB.

## Gate 2: Fake Test Suite

```bash
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate deliver-nanobot-meeting-mvp
```

## Gate 3: Safety

Tests or scans must cover:

- unknown Lark operation rejected,
- write without approval rejected,
- `shell=True` absent in meeting Lark adapter,
- workflow/tool do not call `lark-cli` directly,
- malformed CLI output rejected,
- secrets redacted,
- analyzer output without evidence rejected,
- prompt injection cannot trigger IM write without explicit send-message request.

## Gate 4: Real LLM Dry-run

```bash
scripts/lma-real process \
  --transcript-file tests/fixtures/meeting/transcripts/sample_project_sync.txt \
  --create-doc \
  --create-tasks \
  --dry-run
```

Expected: structured minutes, evidence references, WritePlan, no writes.

## Gate 5: Real lark-cli Dry-run

```bash
scripts/lma-real process \
  --latest-ended \
  --query "项目例会" \
  --create-doc \
  --create-tasks \
  --dry-run
```

Expected: real meeting read, real LLM analysis, WritePlan, no writes.

## Gate 6: Approval-gated Real Writes

```bash
scripts/lma-real approve \
  --run-id <run_id> \
  --operation-ids <op1,op2>
```

Expected: only selected operations execute, results and audit events persist, unapproved operations are skipped.

## Gate 7: Cross-meeting QA

```bash
scripts/lma-real qa --question "上次为什么决定延期上线？"
```

Expected: answer with sources or insufficient evidence.
