## MODIFIED Requirements

### Requirement: Transcript gate workflow
The repository MUST document or provide a helper for verifying real transcript/minutes access.

#### Scenario: Transcript gate ready
- **WHEN** a real provider finds readable transcript or minutes content
- **THEN** the gate reports `ready` and prints the next dry-run process command.

#### Scenario: Transcript gate blocked
- **WHEN** visible meetings have no readable transcript/minutes content
- **THEN** the gate reports `blocked` with checked meeting IDs and blocker reasons.
