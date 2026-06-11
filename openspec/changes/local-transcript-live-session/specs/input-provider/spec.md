## ADDED Requirements

### Requirement: Input provider capabilities

Meeting input providers SHALL expose typed capabilities and typed errors.

#### Scenario: Capability discovery

- **WHEN** a provider session starts
- **THEN** the session SHALL record provider capabilities such as append polling and transcript events.

#### Scenario: Typed provider errors

- **WHEN** a provider receives invalid source paths or invalid session state
- **THEN** it SHALL raise a typed meeting input provider error instead of an unclassified generic failure.

