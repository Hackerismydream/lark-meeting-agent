# Safety Delta

## MODIFIED Requirements

### Requirement: Lark Write Approval
All Lark write operations MUST require explicit approval before execution. Visible live meeting bot join and leave operations MUST be treated as writes.

#### Scenario: Bot join is visible
- **WHEN** the system prepares to join a live meeting
- **THEN** it identifies the operation as visible to meeting participants.
- **AND** real execution requires explicit approval.

#### Scenario: Bot leave is visible
- **WHEN** the system prepares to leave a live meeting
- **THEN** it identifies the operation as visible to meeting participants.
- **AND** real execution requires explicit approval.
