## ADDED Requirements

### Requirement: Sandbox writes are opt-in

All real writes SHALL default to disabled and require `LMA_DEMO_ENABLE_REAL_WRITES=1` plus explicit approval.

#### Scenario: Dry-run default

- **WHEN** a demo is run without `LMA_DEMO_ENABLE_REAL_WRITES=1`
- **THEN** it SHALL generate WritePlan evidence
- **AND** it SHALL NOT execute real Feishu writes

#### Scenario: Missing chat target

- **WHEN** no sandbox chat id is configured
- **THEN** IM operations SHALL be marked `missing_target`
