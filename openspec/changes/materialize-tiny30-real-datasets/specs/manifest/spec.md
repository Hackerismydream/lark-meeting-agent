# Delta for Tiny30 Manifest

## ADDED Requirements

### Requirement: Manifest and Fixture Lock

Tiny30 materialization MUST write manifests and a fixture lock.

#### Scenario: Manifest fields

- GIVEN fixtures are selected
- WHEN manifests are written
- THEN each row includes fixture id, dataset, source id, split, domain, source path, selected reason, license, raw availability, and processed path.

#### Scenario: Fixture lock

- GIVEN dataset manifests exist
- WHEN the fixture lock is built
- THEN `data/manifests/fixture_lock.json` lists datasets, counts, fixture ids, seed, and generated time.
