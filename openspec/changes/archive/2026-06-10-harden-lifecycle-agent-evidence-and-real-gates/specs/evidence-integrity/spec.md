## ADDED Requirements

### Requirement: Transcript-grounded evidence validation
The system MUST validate meeting evidence references against normalized transcript segments after analyzer schema validation.

#### Scenario: Valid evidence
- **WHEN** a decision or action item references an existing segment and uses a quote from that segment
- **THEN** validation succeeds.

#### Scenario: Unknown segment
- **WHEN** a decision or action item references a segment ID that is not in the normalized transcript
- **THEN** validation fails with an evidence validation error.

#### Scenario: Invented quote backfilled
- **WHEN** an evidence ref points to an existing segment but contains a quote not present in that segment
- **THEN** the stored quote is replaced with the exact segment text.

### Requirement: Optional evidence is still checked when present
Risk and open question evidence MAY be optional, but evidence refs that are present MUST be validated against transcript segments.

#### Scenario: Risk evidence checked
- **WHEN** a risk contains an evidence ref with an unknown segment ID
- **THEN** validation fails.
