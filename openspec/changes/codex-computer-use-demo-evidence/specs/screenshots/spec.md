## ADDED Requirements

### Requirement: Screenshots are real artifacts or blockers

The demo pass SHALL save screenshot files for accessible demo artifacts and SHALL write blockers for unavailable or unsafe UI steps.

#### Scenario: UI step cannot be safely captured

- **WHEN** a real Feishu UI contains sensitive data or no demo object exists
- **THEN** the demo pass SHALL NOT fabricate a screenshot
- **AND** it SHALL record a blocker
