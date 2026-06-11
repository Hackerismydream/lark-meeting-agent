## ADDED Requirements

### Requirement: Real Feishu context is sandbox evidence only

Real Feishu reads in this stage SHALL be used only to validate product-chain context, not to ingest private meeting transcript content.

#### Scenario: Calendar read evidence

- **WHEN** the prebrief demo runs with CLI provider
- **THEN** it SHALL read calendar agenda through `LarkToolAdapter`
- **AND** it SHALL write only sanitized calendar evidence
