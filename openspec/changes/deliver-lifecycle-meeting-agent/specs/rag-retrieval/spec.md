## ADDED Requirements

### Requirement: Cross-meeting Retrieval
The system MUST retrieve relevant meeting evidence across meetings using structured filters and text retrieval.

Retrieval filters MUST support project, customer, person, time range, meeting type, and object kind when those fields are available.

#### Scenario: Retrieve historical decision
- **WHEN** the user asks for a past decision about a project
- **THEN** retrieval returns relevant meeting segments, decisions, and memory cards with meeting IDs and segment IDs.

### Requirement: Optional Semantic Retrieval
The system MUST expose an optional semantic retrieval interface without requiring an external vector database in CI.

#### Scenario: Vector backend unavailable
- **WHEN** no vector backend is configured
- **THEN** retrieval falls back to structured and keyword search.

### Requirement: Source-grounded QA
Cross-meeting QA MUST cite sources and MUST refuse unsupported answers.

#### Scenario: Insufficient evidence
- **WHEN** retrieval returns no sufficient evidence
- **THEN** QA returns `insufficient evidence` and no fabricated facts.
