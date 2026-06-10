## ADDED Requirements

### Requirement: Lifecycle MVP truthfulness
Documentation MUST describe the current implementation as a lifecycle local MVP where post-meeting is the most complete closed-loop slice.

#### Scenario: Docs avoid overclaiming
- **WHEN** docs describe live meeting support
- **THEN** they state that live support consumes supplied transcript/event deltas and does not implement automatic bot join or custom ASR.

### Requirement: Fixture metrics are labeled
Documentation MUST label fixture metrics as fixture benchmark metrics, not production deployment metrics.

#### Scenario: Benchmark docs
- **WHEN** delivery docs mention precision or recall
- **THEN** they state the benchmark type and data source.
