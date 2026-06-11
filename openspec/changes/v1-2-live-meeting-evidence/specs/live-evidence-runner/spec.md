## ADDED Requirements

### Requirement: Live evidence runner

The system SHALL provide a live evidence runner for a user-provided 9-digit meeting number.

#### Scenario: Approved live evidence attempt

- **WHEN** the runner is invoked with visible join and leave approval
- **THEN** it SHALL run join dry-run, real join, poll, QA, and leave when possible
- **AND** it SHALL write a sanitized report

#### Scenario: Unapproved visible operations

- **WHEN** approval flags are missing
- **THEN** the runner SHALL NOT perform real join or leave
- **AND** it SHALL write a dry-run-only report
