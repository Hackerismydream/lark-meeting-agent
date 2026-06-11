# Design: V1 Release, Benchmark, and Docs

## Overview

This design implements the `v1-release-benchmark-docs` phase in the V1.0 roadmap.

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

- `docs/V1_RELEASE_REPORT.md`
- `docs/V1_BENCHMARK_REPORT.md`
- `docs/V1_DEMO_RUNBOOK.md`
- `docs/V1_KNOWN_LIMITATIONS.md`
- `docs/V1_RESUME_AND_INTERVIEW_NOTES.md`

### Code

- Documentation-focused phase with minimal code changes.

### Tests

- `tests/meeting/test_docs_truthfulness.py`

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
openspec validate v1-release-benchmark-docs
```

## Rollout

This change may be committed independently. Do not advance to the next phase unless this phase's acceptance gates pass or a concrete blocker is documented.
