# live-lark-listener Specification

## ADDED Requirements

### Requirement: Live Lark Meeting Join
The system MUST support joining an in-progress Lark meeting through the controlled adapter using a 9-digit meeting number.

#### Scenario: Join dry-run
- **WHEN** the user requests a live join dry-run with a meeting number
- **THEN** the adapter returns a preview and does not join the meeting.

#### Scenario: Approved visible join
- **WHEN** the user explicitly approves a real visible join
- **THEN** the adapter executes `vc.meeting.join`.
- **AND** the workflow records the returned long `meeting_id` for later polling and leaving.

### Requirement: Live Lark Event Polling
The system MUST poll live meeting events using the long meeting id returned by join.

#### Scenario: Poll transcript events
- **WHEN** `vc.meeting.events` returns `transcript_received` events
- **THEN** the workflow converts them into live transcript deltas.
- **AND** the live state retains speaker, timestamp, segment id, and evidence.

#### Scenario: Poll pagination token
- **WHEN** the event response returns a `page_token`
- **THEN** the workflow returns and persists the token for later incremental polling.

### Requirement: Live Lark Meeting Leave
The system MUST support leaving a live Lark meeting through the controlled adapter using the long meeting id.

#### Scenario: Leave requires approval
- **WHEN** a real leave is requested without approval
- **THEN** the adapter rejects it before calling the provider.

#### Scenario: Approved visible leave
- **WHEN** the user explicitly approves a real visible leave
- **THEN** the adapter executes `vc.meeting.leave` and records an audit event.

### Requirement: Minutes Independence
The live listener MUST NOT require Feishu/Lark minutes, notes, or paid meeting-minutes availability.

#### Scenario: Live flow without minutes
- **WHEN** a meeting has no readable minutes
- **THEN** the live listener can still ingest events observed while the bot is in the meeting.
