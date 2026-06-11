# Delta for Tiny30 Data Governance

## ADDED Requirements

### Requirement: Raw Data Stays Local

Raw public dataset files MUST NOT be committed.

#### Scenario: Raw data ignore

- GIVEN data is downloaded under `data/raw`
- WHEN git status is checked
- THEN raw dataset files are ignored except `data/raw/README.md`.

### Requirement: Metric Boundary

Tiny30 metrics MUST NOT be described as production Feishu metrics.

#### Scenario: Data report claims

- GIVEN `docs/TINY30_DATA_REPORT.md`
- WHEN it describes tiny30
- THEN it labels results as public corpus development data
- AND it does not claim production Feishu performance.
