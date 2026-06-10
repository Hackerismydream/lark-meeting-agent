# Delta for Memory

## ADDED Requirements

### Requirement: Meeting Knowledge Persistence

The system MUST persist structured meeting knowledge produced by the post-meeting workflow.

Persisted knowledge MUST include meetings, transcript segments, meeting minutes, decisions, action items, risks, open questions, and evidence references.

The implementation SHOULD reuse nanobot session/memory infrastructure where appropriate, but meeting knowledge MUST remain structured and evidence-linked rather than only generic conversational memory.

#### Scenario: Persist after analysis

- GIVEN a meeting has been analyzed successfully
- WHEN PersistKnowledge runs
- THEN the meeting, transcript segments, extracted items, and evidence references are persisted.

### Requirement: Structured Meeting Memory

The system MUST define structured memory records for long-term meeting knowledge.

Memory cards MAY include project memory, customer memory, and people memory.

Each memory card SHOULD include entity_type, entity_id or name, content, confidence, source meeting IDs, and updated_at.

The MVP MAY use local JSONL or workspace-local files.

#### Scenario: Project memory update

- GIVEN multiple meetings contain repeated project risks
- WHEN memory update runs
- THEN the system MAY create or update a project memory card with source meeting references.

### Requirement: Retrieval Interface

The system MUST expose a retrieval interface independent from a specific vector database.

The MVP MAY use keyword-based retrieval or structured filters.

A later change MAY add pgvector or another vector database.

#### Scenario: Retrieval without vector DB

- GIVEN stored meeting knowledge
- WHEN the user asks a historical question
- THEN the MVP can retrieve relevant records using keyword or structured filters
- AND does not require pgvector.

### Requirement: Source-grounded QA

Cross-meeting QA MUST include source references.

The system MUST NOT answer as a confirmed fact when no sufficient evidence is retrieved.

#### Scenario: Historical decision lookup

- GIVEN stored meetings contain a decision about delaying launch
- WHEN the user asks "why did we decide to delay launch"
- THEN the answer includes relevant decision and transcript evidence sources.

#### Scenario: Insufficient evidence

- GIVEN no relevant meeting evidence is retrieved
- WHEN the user asks a historical question
- THEN the system says there is insufficient evidence
- AND does not hallucinate an answer.
