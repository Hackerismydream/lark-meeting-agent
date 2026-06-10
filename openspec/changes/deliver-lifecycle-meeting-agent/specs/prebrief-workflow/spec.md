## ADDED Requirements

### Requirement: PreBriefWorkflow
The system MUST implement a deterministic `PreBriefWorkflow` that prepares meeting context before a meeting starts.

The workflow MUST read calendar agenda, related historical meetings, open action items, related documents, and entity memories through controlled providers and memory stores.

#### Scenario: Generate pre-brief from agenda and memory
- **WHEN** a user requests a pre-brief for a meeting reference
- **THEN** the workflow returns meeting goal, historical background, previous decisions, open action items, risks, open questions, and suggested follow-up questions.
- **AND** every historical claim includes source meeting or document references.

### Requirement: PreBrief Templates
The system MUST support pre-brief templates for at least customer meeting, project sync, requirement review, technical review, incident review, and one-on-one meeting scenarios.

#### Scenario: Customer meeting template
- **WHEN** the meeting type is customer meeting
- **THEN** the pre-brief includes customer context, prior asks, unresolved blockers, promised follow-ups, risks, and recommended questions.

### Requirement: PreBrief Does Not Write
The pre-brief workflow MUST be read-only.

#### Scenario: Pre-brief does not create Lark artifacts
- **WHEN** `PreBriefWorkflow` runs
- **THEN** it MUST NOT create docs, tasks, IM messages, calendar events, or meeting artifacts.
