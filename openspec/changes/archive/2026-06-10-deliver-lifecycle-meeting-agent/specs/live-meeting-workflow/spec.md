## ADDED Requirements

### Requirement: LiveMeetingWorkflow
The system MUST implement `LiveMeetingWorkflow` for in-meeting understanding from incremental transcript segments and meeting events.

The workflow MUST maintain rolling summary, current topic, decision candidates, action item candidates, risks, disagreements, and open questions.

#### Scenario: Ingest transcript delta
- **WHEN** a transcript delta with speaker, timestamp, and text is ingested
- **THEN** the live state is updated without reprocessing the entire meeting transcript.
- **AND** extracted candidates retain source segment IDs.

### Requirement: Live Meeting QA
The system MUST answer in-meeting questions from the current live state and transcript history.

#### Scenario: Ask current commitments
- **WHEN** the user asks who committed to what during the meeting
- **THEN** the answer lists candidate action items with speaker, timestamp, and segment evidence.
- **AND** unsupported answers return insufficient evidence.

### Requirement: Live Workflow Input Boundary
The live workflow MUST consume transcript/event streams supplied by fixtures or adapters and MUST NOT require automatic bot join, custom ASR, or direct VC control.

#### Scenario: Fixture event stream
- **WHEN** a fixture event stream is replayed
- **THEN** live state and live QA results are reproducible without real Lark credentials.
