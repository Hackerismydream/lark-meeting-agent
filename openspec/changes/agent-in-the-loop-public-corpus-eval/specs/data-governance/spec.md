## ADDED Requirements

### Requirement: No external side effects

Agent mode SHALL NOT call real Lark APIs, real Feishu writes, or Computer Use.

#### Scenario: Dry-run writeback only

- **WHEN** PostMeetingWorkflow creates a WritePlan
- **THEN** the runner SHALL assert that every operation is pending dry-run approval
- **AND** it SHALL NOT approve or execute the operations
