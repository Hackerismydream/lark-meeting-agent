## ADDED Requirements

### Requirement: Local transcript privacy boundary

Local transcript live sessions SHALL be explicit and privacy-preserving.

#### Scenario: No hidden capture

- **WHEN** this change is used
- **THEN** it SHALL read only a user-provided transcript file
- **AND** it SHALL NOT implement ScreenCaptureKit, microphone capture, ASR, speaker diarization, or hidden monitoring.

#### Scenario: No Feishu writes

- **WHEN** local transcript input is processed
- **THEN** it SHALL NOT call real Lark
- **AND** it SHALL NOT write to Feishu.

