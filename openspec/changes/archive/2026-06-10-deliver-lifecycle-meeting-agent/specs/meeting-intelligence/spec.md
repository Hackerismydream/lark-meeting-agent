## ADDED Requirements

### Requirement: Lifecycle Schemas
The meeting domain MUST define Pydantic schemas for pre-briefs, live meeting state, live QA answers, entity memories, retrieval results, evaluation cases, and run traces.

#### Scenario: Invalid live answer rejected
- **WHEN** a live answer omits required source metadata
- **THEN** schema validation fails.

### Requirement: Evidence-linked Structured Extraction
Decisions and action items MUST include evidence references in post-meeting and live candidate extraction.

#### Scenario: Candidate action without evidence
- **WHEN** an analyzer returns an action item candidate without evidence
- **THEN** the candidate is rejected or marked incomplete.

### Requirement: No Invented Commitments
The analyzer MUST NOT invent owners, due dates, decisions, or commitments.

#### Scenario: Missing owner
- **WHEN** the transcript contains an action item but no confirmed owner
- **THEN** the action item owner is null or marked unassigned.
