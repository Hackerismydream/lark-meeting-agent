# Delta for Memory

## ADDED Requirements

### Requirement: Implemented Local Meeting Memory

The MVP MUST persist structured meeting knowledge in workspace-local storage.

Persisted data MUST include runs, meetings, transcript segments, minutes, decisions, action items, and run snapshots.

#### Scenario: Persist successful analysis

- GIVEN a workflow run completes analysis
- WHEN memory persistence runs
- THEN JSONL records and a run snapshot are written under `.lark_meeting_agent/`.

### Requirement: Source-grounded QA

The MVP MUST answer historical questions using persisted decisions/action items and evidence.

Responses MUST include meeting IDs and segment IDs when evidence is available.

#### Scenario: QA with sources

- GIVEN meeting memory contains a relevant decision
- WHEN the user asks what was decided
- THEN the answer includes source evidence records.

#### Scenario: QA without sources

- GIVEN no relevant evidence is found
- WHEN the user asks a question
- THEN the answer states insufficient evidence.
