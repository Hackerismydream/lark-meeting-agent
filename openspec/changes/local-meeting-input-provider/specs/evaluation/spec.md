## ADDED Requirements

### Requirement: Local input evaluation

The system SHALL provide deterministic tests for local meeting input providers.

#### Scenario: Tests do not require Feishu credentials

- **WHEN** local provider tests run
- **THEN** they SHALL NOT require real Feishu credentials
- **AND** they SHALL NOT call real Feishu APIs.

#### Scenario: Transcript fidelity

- **WHEN** a local transcript is replayed
- **THEN** every non-empty source segment SHALL produce exactly one transcript event
- **AND** segment ids SHALL remain stable across repeated runs.

