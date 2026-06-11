## ADDED Requirements

### Requirement: Append-only local transcript live session

The system SHALL support a user-initiated live session over an append-only local transcript file.

#### Scenario: New lines become live events

- **WHEN** new transcript lines are appended to the file
- **THEN** the next provider poll SHALL emit new `LiveMeetingEvent` transcript deltas.

#### Scenario: Repeated polls do not duplicate events

- **WHEN** the same session is polled repeatedly without new transcript lines
- **THEN** no duplicate transcript events SHALL be emitted.

#### Scenario: Explicit stop

- **WHEN** the local transcript session is stopped
- **THEN** subsequent polls SHALL not read or emit additional events.

