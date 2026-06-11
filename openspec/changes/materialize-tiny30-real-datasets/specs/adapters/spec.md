# Delta for Tiny30 Adapters

## ADDED Requirements

### Requirement: Real Raw Layout Compatibility

Adapters MUST support the documented real raw layouts for MeetingBank, QMSum, and VCSum in addition to toy samples.

#### Scenario: Dataset path discovery

- GIVEN a raw dataset checkout or extraction under `data/raw/<dataset>`
- WHEN the corresponding prepare script runs
- THEN it discovers known data files and emits valid fixtures.

### Requirement: Deterministic Selection

Preparation MUST be deterministic.

#### Scenario: Repeatable tiny10

- GIVEN the same raw data, limit, and seed
- WHEN a prepare script runs twice
- THEN it selects the same source records in the same order.
