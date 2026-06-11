## ADDED Requirements

### Requirement: Local audio file provider

The system SHALL provide a local audio file provider for explicit user-selected audio files.

#### Scenario: Audio file with transcript sidecar

- **WHEN** an audio file and transcript sidecar are supplied
- **THEN** the provider SHALL validate the audio file path
- **AND** normalize the transcript sidecar into canonical events and segments.

#### Scenario: Audio file without ASR

- **WHEN** an audio file is supplied without transcript text
- **THEN** the provider SHALL NOT fabricate transcript content
- **AND** it SHALL emit only a marker event that the audio file is registered and awaiting transcription.

#### Scenario: Live capture out of scope

- **WHEN** this change is implemented
- **THEN** it SHALL NOT implement ScreenCaptureKit live system-audio capture
- **AND** it SHALL NOT implement microphone live streaming.

