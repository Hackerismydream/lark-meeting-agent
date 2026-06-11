# Design: Real Live Meeting Smoke Gate

## Overview

This design implements the `real-live-meeting-smoke` phase in the V1.0 roadmap.

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

- `docs/LIVE_LARK_SMOKE_RUNBOOK.md`
- `docs/LIVE_LARK_SMOKE_RESULTS.md`
- `docs/REAL_LIVE_GATE.md`

### Code

- `scripts/lma-real`
- `nanobot/meeting/live_lark.py`

### Tests

- `tests/meeting/test_real_smoke_scripts.py`

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
openspec validate real-live-meeting-smoke
```

## Rollout

This change may be committed independently. Do not advance to the next phase unless this phase's acceptance gates pass or a concrete blocker is documented.
