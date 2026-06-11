# Delta for Meeting Data Sources

## ADDED Requirements

### Requirement: Supported Public Meeting Datasets

The system MUST support MeetingBank, QMSum, and VCSum as development and evaluation data sources.

#### Scenario: Dataset support is scoped

- GIVEN the meeting data bootstrap change
- WHEN dataset adapters are implemented
- THEN MeetingBank, QMSum, and VCSum are supported
- AND AMI, ICSI, audio files, and ASR are not introduced.

### Requirement: Raw Dataset Governance

Raw public datasets MUST NOT be committed to git.

#### Scenario: Missing raw data

- GIVEN a preparation script is run without the required raw dataset directory
- WHEN it checks inputs
- THEN it fails with clear download instructions
- AND it does not fail with an obscure parser or file error.
