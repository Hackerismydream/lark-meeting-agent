# Design: Security, Admin, and Governance

## Overview

This design implements the `security-admin-governance` phase in the V1.0 roadmap.

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

- `docs/PRODUCTION_SECURITY_CHECKLIST.md`
- `docs/ADMIN_GUIDE.md`
- `docs/RED_TEAM_CASES.md`

### Code

- `nanobot/meeting/security.py`
- `nanobot/meeting/production.py`
- `nanobot/meeting/lark_adapter.py`

### Tests

- `tests/meeting/test_security_governance.py`
- `tests/meeting/test_red_team_cases.py`

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
openspec validate security-admin-governance
```

## Rollout

This change may be committed independently. Do not advance to the next phase unless this phase's acceptance gates pass or a concrete blocker is documented.
