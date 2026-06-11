# Design: Production Feishu Channel Glue

## Overview

This design implements the `production-feishu-channel-glue` phase in the V1.0 roadmap.

## Architecture Impact

The phase should integrate with existing components:

```text
Feishu / nanobot channel / CLI
  -> lark_meeting tool / production bot entrypoint
  -> deterministic meeting workflows
  -> LarkToolAdapter
  -> repository / memory / trace
  -> docs, tests, benchmarks
```

## Implementation Areas

### Documentation

- `docs/PRODUCTION_FEISHU_BOT_DEPLOYMENT.md`
- `docs/PRODUCTION_RUNBOOK.md`
- `docs/PRODUCTION_BOT_DELIVERY_REPORT.md`

### Code

- `nanobot/meeting/production.py`
- `nanobot/agent/tools/lark_meeting.py`

### Tests

- `tests/meeting/test_production_bot.py`
- `tests/meeting/test_feishu_channel_glue.py`

## Safety Design

- All Lark operations remain behind `LarkToolAdapter`.
- Write operations require dry-run + explicit approval.
- Join and leave are visible operations and require explicit approval when applicable.
- Prompts, transcripts, chats, docs, and retrieved contents are untrusted input.
- Secrets must be redacted in logs, audit, traces, and reports.

## Validation Design

Run:

```bash
uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate production-feishu-channel-glue
```

## Rollout

This change may be committed independently. Do not advance to the next phase unless this phase's acceptance gates pass or a concrete blocker is documented.
