# Workflows Spec

## Purpose

Define deterministic meeting workflow behavior.
## Requirements
### Requirement: Lifecycle Workflow Router
The meeting domain MUST route lifecycle actions to deterministic workflow classes rather than autonomous free-form tool planning.

#### Scenario: Route prebrief action
- **WHEN** the nanobot tool receives `action="prebrief"`
- **THEN** it calls `PreBriefWorkflow` and returns a serialized pre-brief result.

### Requirement: PostMeetingWorkflow Compatibility
The lifecycle change MUST preserve existing post-meeting process, approve, QA, and status behavior.

#### Scenario: Existing fixture process still works
- **WHEN** the existing sample transcript fixture is processed
- **THEN** the system still returns structured minutes, evidence-linked decisions/actions, a write plan, and persisted memory.

### Requirement: MemoryWorkflow
The system MUST implement a memory workflow that consolidates meeting outputs into meeting, project, customer, person, action, decision, risk, question, and memory-card records.

#### Scenario: Consolidate completed meeting
- **WHEN** a post-meeting run completes
- **THEN** the memory workflow writes or updates structured memory records and retrieval indexes.
