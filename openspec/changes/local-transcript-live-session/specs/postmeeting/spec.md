## ADDED Requirements

### Requirement: Optional post-meeting finalization

The local transcript live runner SHALL optionally generate post-meeting minutes and a dry-run write plan from accumulated transcript.

#### Scenario: Dry-run WritePlan

- **WHEN** finalization is requested after local transcript events were ingested
- **THEN** the runner SHALL generate meeting minutes from accumulated `TranscriptSegment` objects
- **AND** it SHALL generate a dry-run write plan without calling real Lark.

