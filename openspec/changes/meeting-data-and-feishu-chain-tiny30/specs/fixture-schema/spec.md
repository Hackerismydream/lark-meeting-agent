# Delta for Canonical Fixture Schema

## ADDED Requirements

### Requirement: MeetingFixture Schema Integrity

The system MUST define a canonical `MeetingFixture` schema for all supported public meeting datasets.

#### Scenario: Fixture validation

- GIVEN a fixture from MeetingBank, QMSum, or VCSum
- WHEN it is validated
- THEN it has a fixture id, supported dataset value, provenance, and non-empty transcript turns
- AND turn ids, agenda ids, and query ids are unique inside the fixture
- AND query relevant turn ids refer to existing transcript turns.

### Requirement: Optional Action and Decision Labels

Action item and decision labels MUST be optional for public dataset fixtures.

#### Scenario: Dataset lacks action labels

- GIVEN a public meeting dataset does not provide strict action item or decision labels
- WHEN the fixture is built
- THEN expected action items and decisions may be empty
- AND schema validation still succeeds when transcript and provenance are valid.
