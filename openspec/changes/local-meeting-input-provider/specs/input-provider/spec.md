## ADDED Requirements

### Requirement: Provider-agnostic meeting input

The system SHALL support a provider-agnostic meeting input interface with start, poll, and stop operations.

#### Scenario: Canonical events

- **WHEN** any meeting input provider emits meeting content
- **THEN** it SHALL output canonical `LiveMeetingEvent` objects
- **AND** transcript-bearing providers SHALL also expose canonical `TranscriptSegment` objects in the event batch.

#### Scenario: Feishu official listener remains supported

- **WHEN** local providers are added
- **THEN** the Feishu official live listener SHALL remain supported as an input path
- **AND** it SHALL NOT be removed or replaced by local providers.

