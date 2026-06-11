# Meeting Data Evaluation Tasks

## Shared Metrics

- `schema_valid_rate`
- `workflow_completion_rate`
- `evidence_coverage`
- `unsupported_claim_count`
- `span_recall`
- `span_precision`
- `source_attribution_rate`
- `trace_completeness`
- `artifact_consistency`
- `streaming_stability`
- `memory_write_validity`

## MeetingBank

- `agenda_coverage`
- `segment_summary_similarity`
- `evidence_from_correct_agenda`

## QMSum

- `query_answer_schema_valid`
- `relevant_span_recall`
- `relevant_span_precision`
- `insufficient_evidence_correctness`

## VCSum

- `chinese_schema_stability`
- `topic_boundary_similarity`
- `salient_evidence_recall`

These metrics are deterministic gates. ROUGE, BERTScore, LLM judges, or external benchmark tools can be added later as optional reports, not required gates.
