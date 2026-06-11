# Delta for Tiny30 Fixture Schema

## ADDED Requirements

### Requirement: Canonical Fixture Validation

Generated tiny30 fixtures MUST validate as canonical `MeetingFixture` objects.

#### Scenario: Generated fixture validation

- GIVEN a generated tiny30 fixture
- WHEN `MeetingFixture` validates it
- THEN provenance is present
- AND transcript turns are non-empty
- AND turn, query, and agenda ids are unique
- AND query relevant turn references exist.
