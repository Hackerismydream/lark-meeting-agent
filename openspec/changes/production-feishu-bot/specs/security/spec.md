## ADDED Requirements

### Requirement: Meeting-agent access policy
The production bot MUST enforce meeting-agent authorization in addition to nanobot Feishu channel `allowFrom` and group policy.

#### Scenario: Denied user
- **WHEN** a sender is not in allowed users, admin users, or allowed chat policy
- **THEN** the bot rejects the request with a safe message and records a denied audit event.

### Requirement: Approver policy
Write approval MUST be accepted only from configured write approvers or admins.

#### Scenario: Non-approver approve attempt
- **WHEN** a non-approver sends `/meeting approve <run_id> <operation_id>`
- **THEN** the bot rejects the approval and executes no write operations.

### Requirement: Production safety defaults
Production configs MUST recommend `tools.exec.enable=false`, `tools.restrictToWorkspace=true`, explicit approver lists, dry-run defaults, and no wildcard `allowFrom` unless explicitly intended.

#### Scenario: Unsafe config detected
- **WHEN** production config uses wildcard allow or enables exec without an explicit override
- **THEN** validation reports a safety warning.
