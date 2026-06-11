## ADDED Requirements

### Requirement: Live evidence privacy boundary

Live evidence packs SHALL be sanitized and local-run artifacts SHALL NOT be committed by default.

#### Scenario: Raw provider output

- **WHEN** raw provider output contains credentials or private IDs
- **THEN** the stored report SHALL redact sensitive values
