# Delta for Meeting Intelligence

## ADDED Requirements

### Requirement: Implemented Transcript Normalization

The system MUST normalize transcript text into ordered `TranscriptSegment` records with stable segment IDs, meeting ID, text, and available speaker/timestamp fields.

#### Scenario: Timestamped speaker transcript

- GIVEN transcript lines contain timestamps and speakers
- WHEN normalization runs
- THEN output segments preserve order, speaker names, timestamps, and text.

### Requirement: Implemented Analyzer Modes

The system MUST provide deterministic fake analysis for CI and OpenAI-compatible LLM analysis for real demos.

LLM analysis MUST validate output with Pydantic schemas before any write plan is generated.

#### Scenario: Fake analyzer output

- GIVEN the sample project-sync transcript
- WHEN fake analysis runs
- THEN it produces schema-valid minutes, decisions, action items, risks, and open questions.

### Requirement: Evidence Enforcement

Every decision and action item MUST include at least one evidence reference.

Analyzer output without required evidence MUST be rejected by schema validation.

#### Scenario: Missing evidence rejected

- GIVEN a decision or action item lacks evidence references
- WHEN schema validation runs
- THEN validation fails.

### Requirement: No Fabricated Commitments

The system MUST NOT invent owners, due dates, decisions, or commitments that are not supported by evidence.

Unknown owners MUST be `None` or `unassigned`. Unknown due dates MUST be `None`.

#### Scenario: Unknown due date

- GIVEN the evidence does not contain an exact due date
- WHEN an action item is extracted
- THEN `due_date` remains null.
