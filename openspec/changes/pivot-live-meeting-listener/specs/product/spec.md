# Product Delta

## MODIFIED Requirements

### Requirement: Lifecycle Product Contract
The product MUST be described as a Lark meeting workflow agent whose primary real transcript acquisition path is live meeting listening, with historical minutes/notes used only as optional enrichment.

#### Scenario: Product positioning
- **WHEN** documentation describes the lifecycle agent
- **THEN** it distinguishes live meeting listening from post-meeting paid minutes retrieval.
- **AND** it does not treat missing readable minutes as a product blocker.

### Requirement: Current Capability Honesty
Documentation MUST distinguish fixture validation, real DeepSeek validation, live meeting listener capability, and account-dependent historical minutes availability.

#### Scenario: Real Lark blocker documented
- **WHEN** real Lark minutes are not readable for the current account
- **THEN** docs state that this only blocks optional historical minutes enrichment.
- **AND** docs point the primary real gate to live join and live event polling.
