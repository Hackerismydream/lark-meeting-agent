## ADDED Requirements

### Requirement: Layered Meeting Memory
The system MUST persist raw transcript segments, structured minutes, decisions, action items, risks, open questions, memory cards, entity memories, and run snapshots in layered storage.

#### Scenario: Persist entity memory
- **WHEN** a workflow identifies a customer concern from supported evidence
- **THEN** it stores an entity memory card with source meeting IDs.

### Requirement: Open Action Item Index
The memory store MUST support querying open action items by meeting, project, customer, person, status, and due date when available.

#### Scenario: Pre-brief open actions
- **WHEN** a pre-brief is generated for a project meeting
- **THEN** relevant open action items are included with sources.

### Requirement: Backward Compatibility
The memory store MUST continue reading current post-meeting MVP JSONL and run snapshot artifacts.

#### Scenario: Load old run snapshot
- **WHEN** a snapshot produced by the post-meeting MVP is loaded
- **THEN** lifecycle memory code can read it without migration failure.
