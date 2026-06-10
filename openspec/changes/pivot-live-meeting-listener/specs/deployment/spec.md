# Deployment Delta

## MODIFIED Requirements

### Requirement: Real Transcript Gate
The real transcript gate MUST prioritize live meeting listener validation over account-dependent historical minutes access.

#### Scenario: Live listener gate
- **WHEN** a currently running 9-digit meeting number is available
- **THEN** the operator can run the live join, event poll, live QA, and leave smoke flow.
- **AND** the pass condition is live transcript/chat event ingestion with source-grounded state, not readable post-meeting minutes.
