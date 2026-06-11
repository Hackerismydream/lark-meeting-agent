# Delta for Dataset Adapters

## ADDED Requirements

### Requirement: Dataset Adapter Outputs

Each dataset adapter MUST convert raw or toy source records into canonical `MeetingFixture` objects.

#### Scenario: Toy samples

- GIVEN toy raw samples under `tests/fixtures/meeting_data/raw_samples`
- WHEN MeetingBank, QMSum, and VCSum adapters run
- THEN each adapter emits valid fixtures
- AND tests do not require full raw datasets.

### Requirement: Deterministic Sampling and Manifests

Tiny10 selection MUST be deterministic and manifest-backed.

#### Scenario: Manifest fields

- GIVEN selected fixture records
- WHEN the manifest is written
- THEN every record includes fixture id, dataset, source id, split, domain, source path, selected reason, license, processed path, and raw availability.
