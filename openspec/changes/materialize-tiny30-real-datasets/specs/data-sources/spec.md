# Delta for Tiny30 Data Sources

## ADDED Requirements

### Requirement: Stage Scope

The system MUST materialize tiny30 fixtures from MeetingBank, QMSum, and VCSum only.

#### Scenario: No unrelated data source

- GIVEN Stage 1 execution
- WHEN data preparation runs
- THEN it uses MeetingBank, QMSum, and VCSum
- AND it does not add AMI, ICSI, audio processing, ASR, Feishu, or LLM calls.

### Requirement: Missing Raw Data Instructions

Preparation scripts MUST fail with clear download instructions when raw data is missing.

#### Scenario: Missing raw directory

- GIVEN the raw dataset directory does not exist
- WHEN a prepare script runs
- THEN it exits non-zero with dataset-specific download commands
- AND it does not emit an obscure stack trace.
