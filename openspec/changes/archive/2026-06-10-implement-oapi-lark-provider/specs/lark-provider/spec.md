## MODIFIED Requirements

### Requirement: Provider strategy
The system MUST distinguish fake, CLI, and OpenAPI provider roles.

#### Scenario: OAPI provider is available behind adapter
- **WHEN** the configured provider mode is `oapi`
- **THEN** workflows obtain Lark access through `LarkToolAdapter.oapi`.

### Requirement: OpenAPI provider plan
The production bot MUST include an `OapiLarkProvider` design or implementation plan before claiming production Lark provider readiness.

#### Scenario: OAPI provider implemented
- **WHEN** `OapiLarkProvider` is configured with an access token
- **THEN** allowlisted operations are translated into Lark OpenAPI HTTP requests behind `LarkToolAdapter`.

### Requirement: Adapter boundary preserved
All providers MUST remain behind `LarkToolAdapter`.

#### Scenario: OAPI request path
- **WHEN** a workflow uses provider mode `oapi`
- **THEN** it calls `LarkToolAdapter` and does not call HTTP APIs directly.
