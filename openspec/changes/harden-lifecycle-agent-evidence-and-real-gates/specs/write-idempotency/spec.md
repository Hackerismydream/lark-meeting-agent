## ADDED Requirements

### Requirement: Run provider binding
The system MUST persist process provider mode and analyzer mode in run snapshots and use the stored provider mode for approval by default.

#### Scenario: Approve uses stored provider
- **WHEN** a run snapshot was created with provider mode `cli`
- **THEN** approve uses `cli` unless an explicit provider override is supplied.

#### Scenario: Provider mismatch rejected
- **WHEN** a caller supplies a provider mode that differs from the stored run provider without explicit override
- **THEN** approval is rejected.

### Requirement: Write operation idempotency
The system MUST prevent duplicate execution of already completed write operations.

#### Scenario: Repeated approval
- **WHEN** an operation has execution status `completed`
- **THEN** a later approval for the same operation ID keeps the existing result and does not call the Lark provider again.

### Requirement: Stable idempotency keys
Every generated write operation MUST include a stable idempotency key based on run ID, operation type, operation ID, and payload.

#### Scenario: Operation key exists
- **WHEN** a write plan is generated
- **THEN** every operation contains a non-empty idempotency key.
