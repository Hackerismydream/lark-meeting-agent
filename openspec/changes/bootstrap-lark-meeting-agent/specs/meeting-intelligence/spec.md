# Delta for Meeting Intelligence

## ADDED Requirements

### Requirement: Transcript Normalization

The system MUST normalize all transcript inputs into ordered `TranscriptSegment` objects.

Each segment MUST include segment_id, meeting_id, and text.

Each segment SHOULD include speaker_name, speaker_id, start_time, and end_time when available.

#### Scenario: Timestamped transcript

- GIVEN a transcript contains speaker names and timestamps
- WHEN the transcript is normalized
- THEN each segment preserves speaker and timestamp information.

#### Scenario: Untimestamped transcript

- GIVEN a transcript has no timestamps
- WHEN the transcript is normalized
- THEN the system still creates ordered segments
- AND timestamp fields remain null.

### Requirement: Structured Meeting Minutes

The system MUST generate meeting minutes as a validated schema.

Meeting minutes MUST include title, one_sentence_summary, detailed_summary, chapters, decisions, action_items, risks, and open_questions.

All LLM-produced meeting intelligence outputs MUST be validated by typed Pydantic schemas before use by workflows, APIs, storage, or write planning.

#### Scenario: Valid minutes output

- GIVEN a valid transcript
- WHEN the analyzer runs
- THEN it returns a valid `MeetingMinutes` object
- AND no unstructured free-form response is returned as the final system output.

#### Scenario: Invalid analyzer output

- GIVEN an analyzer returns malformed meeting minutes
- WHEN schema validation runs
- THEN the output is rejected with `AnalyzerValidationError`
- AND no write plan is generated from the malformed output.

### Requirement: Evidence Preservation

Every decision and action item MUST include at least one `EvidenceRef`.

Evidence references MUST point to source transcript segments.

#### Scenario: Decision extraction

- GIVEN a transcript segment contains a clear decision
- WHEN the analyzer extracts that decision
- THEN the decision includes the source segment ID
- AND includes speaker and timestamp if available.

#### Scenario: Unsupported decision

- GIVEN a generated decision has no supporting transcript segment
- WHEN validation runs
- THEN the decision is rejected or marked incomplete
- AND is not presented as a confirmed decision.

### Requirement: No Hallucinated Owners

The system MUST NOT invent owners for action items.

If owner cannot be inferred from evidence, owner MUST be null or `unassigned`.

#### Scenario: Missing owner

- GIVEN a transcript says "需要补充接口文档"
- WHEN no owner is mentioned
- THEN the extracted action item owner is null or `unassigned`
- AND the system does not invent a person.

### Requirement: Due Date Resolution

The system MUST support due date resolution semantics for action items.

The system MAY resolve relative due dates when meeting date is known.

If due date cannot be inferred, due_date MUST be null.

#### Scenario: Relative date

- GIVEN a meeting on 2026-06-09
- AND a transcript says "周五前补充接口文档"
- WHEN due date resolution runs
- THEN the due date is resolved according to the meeting date.

#### Scenario: No due date evidence

- GIVEN an action item has no due date evidence
- WHEN it is extracted
- THEN due_date remains null.
