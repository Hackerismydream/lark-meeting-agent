## ADDED Requirements

### Requirement: Public corpus metric scope

Reports from agent mode SHALL set `metric_scope` to `public_corpus_development`.

#### Scenario: Metrics are not production claims

- **WHEN** a report is generated
- **THEN** it SHALL distinguish public corpus development metrics from real Lark smoke evidence and production metrics
- **AND** it SHALL record whether real LLM was used

### Requirement: Agent mode metric fields

Agent mode reports SHALL include workflow completion, evidence coverage, source attribution, streaming stability, memory write validity, and write plan dry-run rate.

#### Scenario: Required metric fields are present

- **WHEN** agent mode writes `report.json`
- **THEN** the report metrics SHALL include `workflow_completion_rate`, `evidence_coverage`, `source_attribution_rate`, `streaming_stability`, `memory_write_validity`, and `write_plan_dry_run_rate`
