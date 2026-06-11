# Design: Production Storage and Run State

## Overview

This design implements the `production-storage-run-state` phase in the V1.0 roadmap.

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

- `docs/STORAGE_RUN_STATE.md`
- `docs/STORAGE_MIGRATION_PLAN.md`
- `docs/RUN_RECOVERY_RUNBOOK.md`

### Code

- `nanobot/meeting/repository.py`
- `nanobot/meeting/workflow.py`
- `nanobot/meeting/production.py`

### Tests

- `tests/meeting/test_repository.py`
- `tests/meeting/test_run_state_recovery.py`

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
openspec validate production-storage-run-state
```

## Rollout

This change may be committed independently. Do not advance to the next phase unless this phase's acceptance gates pass or a concrete blocker is documented.
