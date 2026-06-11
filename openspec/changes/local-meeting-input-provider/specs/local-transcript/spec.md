## ADDED Requirements

### Requirement: Local transcript provider

The system SHALL provide a local transcript provider that reads an explicit user-selected transcript file and replays it into the live meeting pipeline.

#### Scenario: Text transcript replay

- **WHEN** a local text transcript is supplied
- **THEN** the provider SHALL normalize it into `TranscriptSegment` objects
- **AND** poll SHALL emit corresponding `transcript_delta` `LiveMeetingEvent` objects.

#### Scenario: No direct Feishu writes

- **WHEN** the local transcript provider processes input
- **THEN** it SHALL NOT write to Feishu directly.

