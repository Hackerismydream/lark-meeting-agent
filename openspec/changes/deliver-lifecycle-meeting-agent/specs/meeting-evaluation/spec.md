## ADDED Requirements

### Requirement: Lifecycle Benchmark
The system MUST include a reproducible benchmark for meeting lifecycle behavior.

The benchmark MUST cover transcript normalization, structured extraction, evidence consistency, action synchronization planning, tool safety, and QA citation accuracy.

#### Scenario: Run lifecycle benchmark
- **WHEN** the lifecycle evaluation command runs against bundled fixtures
- **THEN** it outputs machine-readable metrics for each evaluation layer.

### Requirement: Extraction Metrics
The benchmark MUST compute action item precision, action item recall, decision precision, decision recall, evidence coverage, and schema validation success rate.

#### Scenario: Action item metrics
- **WHEN** predicted action items are compared against expected fixture labels
- **THEN** the report includes precision and recall.

### Requirement: Resume Metric Gates
The benchmark MUST include an acceptance profile aligned to resume claims.

The target profile MUST require action item precision of at least 90%, action item recall of at least 85%, evidence coverage of 100%, and safety regression pass rate of 100% on the fixture benchmark.

#### Scenario: Acceptance profile failure
- **WHEN** any target metric falls below threshold
- **THEN** the evaluation command exits non-zero or marks the profile failed.
