# V1 Benchmark Report

Commit: `dd31286`

Fixture version:

- `tests/fixtures/meeting/evaluation/lifecycle_cases.json`
- `tests/fixtures/meeting/scenarios/`

Model profile:

- deterministic fake analyzer/provider,
- no real LLM benchmark in this report,
- no real Lark dependency in normal tests.

## Deterministic Fixture Metrics

Lifecycle evaluation command:

```bash
uv run python -m nanobot.meeting.cli evaluate \
  --cases tests/fixtures/meeting/evaluation/lifecycle_cases.json \
  --output /tmp/lma-v1-lifecycle-eval.json
```

Result:

- cases: 31
- action precision: 1.0
- action recall: 1.0
- decision precision: 1.0
- decision recall: 1.0
- evidence coverage: 1.0
- schema validation success rate: 1.0
- tool call success rate: 1.0
- QA source accuracy: 1.0
- safety pass rate: 1.0

Live replay command:

```bash
uv run python - <<'PY'
from nanobot.meeting.evals_live import LiveReplayEvaluator
report = LiveReplayEvaluator('/tmp/lma-v1-live-workspace').evaluate_dir(
    'tests/fixtures/meeting/scenarios',
    metrics_output='/tmp/lma-v1-live-metrics.json',
    failures_output='/tmp/lma-v1-live-failures.json',
)
print(report.model_dump_json(indent=2))
PY
```

Result:

- scenarios: 8
- action item precision: 0.9375
- action item recall: 1.0
- decision precision: 1.0
- decision recall: 1.0
- evidence coverage: 1.0
- QA source accuracy: 1.0
- approval bypass rate: 0.0
- duplicate event count: 1
- malformed event count: 1
- failures: 0

## Optional Real LLM Metrics

Not run for this V1 release report. Do not treat deterministic fake metrics as real LLM quality metrics.

## Real Lark Smoke

Not run in Phase 10. Earlier phases added opt-in `scripts/lma-real live-smoke`, but this report does not claim a real meeting join/poll/QA/leave success.

## Validation Command Results

Final Phase 10 validation results are recorded in `docs/V1_PHASE_10_DELIVERY_REPORT.md`.
