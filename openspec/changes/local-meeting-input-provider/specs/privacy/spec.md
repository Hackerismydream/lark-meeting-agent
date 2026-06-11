## ADDED Requirements

### Requirement: Local input privacy boundary

Local meeting input providers SHALL be explicit, user-initiated, and privacy-preserving.

#### Scenario: No hidden monitoring

- **WHEN** local input providers are used
- **THEN** they SHALL require explicit file paths or explicit future capture consent
- **AND** they SHALL NOT implement hidden monitoring.

#### Scenario: Feishu writeback remains gated

- **WHEN** local input produces meeting content
- **THEN** it SHALL NOT bypass existing `WritePlan` approval
- **AND** all Feishu writeback SHALL remain gated through `LarkToolAdapter`.

