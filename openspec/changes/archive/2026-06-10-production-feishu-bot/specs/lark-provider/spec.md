## ADDED Requirements

### Requirement: Provider strategy
The system MUST distinguish fake, CLI, and OpenAPI provider roles.

#### Scenario: CI uses fake provider
- **WHEN** fake tests run
- **THEN** no real Lark credentials are required.

#### Scenario: CLI provider is diagnostic
- **WHEN** local real smoke is run
- **THEN** `CliLarkProvider` MAY be used with explicit limitations documented.

### Requirement: OpenAPI provider plan
The production bot MUST include an `OapiLarkProvider` design or implementation plan before claiming production Lark provider readiness.

#### Scenario: Provider not implemented
- **WHEN** `OapiLarkProvider` is not implemented
- **THEN** docs MUST state that production provider support remains planned.

### Requirement: Adapter boundary preserved
All providers MUST remain behind `LarkToolAdapter`.

#### Scenario: Workflow needs Lark operation
- **WHEN** a workflow needs a Lark read or write
- **THEN** it calls `LarkToolAdapter`, not `lark-cli`, HTTP APIs, or SDKs directly.
