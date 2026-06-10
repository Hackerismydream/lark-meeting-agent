# Design: Testing Strategy and Live Meeting Simulator

## Overview

This design implements the `testing-strategy-live-simulator` phase in the V1.0 roadmap.

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

- `docs/TESTING_STRATEGY.md`
- `docs/FIXTURE_GUIDE.md`
- `docs/LIVE_SIMULATOR.md`
- `docs/EVALUATION_METRICS.md`
- `docs/LIVE_LARK_SMOKE_RUNBOOK.md`
- `docs/ASR_TESTING.md`
- `docs/OSS_TOOLING_DECISIONS.md`
- `docs/TESTING_INFRA_DELIVERY_REPORT.md`

### Code

- `nanobot/meeting/simulator.py`
- `nanobot/meeting/evals_live.py`
- `nanobot/meeting/evals_lifecycle.py`
- `nanobot/meeting/metrics.py`

### Tests

- `tests/meeting/test_live_simulator.py`
- `tests/meeting/test_live_event_replay.py`
- `tests/meeting/test_event_conversion_contract.py`
- `tests/meeting/test_event_conversion_fuzz.py`
- `tests/meeting/test_lifecycle_replay.py`
- `tests/meeting/test_prebrief_scenarios.py`
- `tests/meeting/test_postmeeting_scenarios.py`
- `tests/meeting/test_qa_source_metrics.py`
- `tests/meeting/test_tool_safety_matrix.py`

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
openspec validate testing-strategy-live-simulator
```

## Rollout

This change may be committed independently. Do not advance to the next phase unless this phase's acceptance gates pass or a concrete blocker is documented.
