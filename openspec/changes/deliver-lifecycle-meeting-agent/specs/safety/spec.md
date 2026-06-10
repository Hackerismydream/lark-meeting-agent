## ADDED Requirements

### Requirement: Transcript Injection Boundary
Meeting transcripts, documents, agenda text, and IM messages MUST be treated as untrusted content.

#### Scenario: Malicious transcript asks to send IM
- **WHEN** transcript text contains instructions to bypass approval and send a message
- **THEN** no write operation executes and no unrequested IM write is planned.

### Requirement: Approval Token Boundary
Approved write execution MUST require selected operation IDs from a persisted write plan.

#### Scenario: Forged approval target
- **WHEN** an approval request references an operation ID not present in the run snapshot
- **THEN** the workflow rejects or ignores that operation.

### Requirement: Safety Regression Suite
The test suite MUST cover unknown tool rejection, unapproved write rejection, malicious transcript injection, malformed tool output, trace redaction, and approval selection.

#### Scenario: Safety tests pass
- **WHEN** the safety regression suite runs
- **THEN** all configured safety cases pass without real credentials.
