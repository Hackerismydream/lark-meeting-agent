## ADDED Requirements

### Requirement: Local transcript events feed live workflow

Local transcript session events SHALL feed `LiveMeetingWorkflow`.

#### Scenario: Live state updates

- **WHEN** the listener runner polls new local transcript events
- **THEN** it SHALL ingest them into `LiveMeetingWorkflow`
- **AND** the live state SHALL contain transcript segments and candidate evidence.

#### Scenario: Live QA

- **WHEN** the user asks a question against the local transcript live session
- **THEN** the system SHALL answer with sources from live state or return insufficient evidence.

