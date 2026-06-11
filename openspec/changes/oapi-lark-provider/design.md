# Design: Production Lark OpenAPI Provider

## Overview

This design implements the `oapi-lark-provider` phase in the V1.0 roadmap.

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

- `docs/OAPI_PROVIDER_PLAN.md`
- `docs/OAPI_PROVIDER_DELIVERY_REPORT.md`
- `docs/LARK_PROVIDER_STRATEGY.md`

### Code

- `nanobot/meeting/lark_oapi_provider.py`
- `nanobot/meeting/lark_adapter.py`

### Tests

- `tests/meeting/test_oapi_lark_provider.py`
- `tests/meeting/test_lark_adapter.py`

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
openspec validate oapi-lark-provider
```

## Rollout

This change may be committed independently. Do not advance to the next phase unless this phase's acceptance gates pass or a concrete blocker is documented.
