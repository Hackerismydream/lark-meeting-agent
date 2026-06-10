# Evaluation Metrics

Phase 1 metrics are deterministic fixture metrics. They are not production metrics.

Implemented metrics:

- `action_item_precision`
- `action_item_recall`
- `decision_precision`
- `decision_recall`
- `evidence_coverage`
- `evidence_grounding_accuracy`
- `qa_source_accuracy`
- `live_summary_freshness`
- `owner_hallucination_rate`
- `due_date_hallucination_rate`
- `tool_call_safety_pass_rate`
- `approval_bypass_rate`
- `write_plan_correctness`
- `regression_stability`
- `duplicate_event_count`
- `malformed_event_count`

Reports can be written to:

```text
/tmp/lma-live-eval.json
/tmp/lma-live-eval-failures.json
```

LLM-as-judge is not used as the only source of truth. Gold labels live in fixture `expected.json` files.
