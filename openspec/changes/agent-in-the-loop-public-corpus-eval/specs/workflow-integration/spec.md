## ADDED Requirements

### Requirement: Public corpus fixtures exercise Agent workflows

Agent mode SHALL invoke pre-brief, live replay, post-meeting, QA, WritePlan, and memory persistence behavior for each fixture.

#### Scenario: Fixture produces workflow artifacts

- **WHEN** a fixture is evaluated in agent mode
- **THEN** prebrief, live snapshots, minutes, QA answers, and write plan artifacts SHALL be created
- **AND** WritePlan operations SHALL remain dry-run / unapproved

### Requirement: Agent mode is eval-local

Agent mode SHALL use per-run local workspaces and SHALL NOT pollute the user's real meeting memory.

#### Scenario: Memory writes stay under eval run

- **WHEN** a fixture is evaluated in agent mode
- **THEN** meeting memory SHALL be written under the fixture run directory
- **AND** no user workspace Lark memory directory SHALL be required
