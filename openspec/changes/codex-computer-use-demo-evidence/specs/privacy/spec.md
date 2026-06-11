## ADDED Requirements

### Requirement: Screenshots avoid secrets and private content

Screenshots SHALL NOT display access tokens, app secrets, cookies, unrelated private chats, unrelated calendars, or real customer names unless explicitly sandbox.

#### Scenario: Local fallback screenshot

- **WHEN** real Feishu UI cannot be safely captured
- **THEN** local public-fixture or dry-run artifacts MAY be captured instead
- **AND** the report SHALL label them as local/dry-run evidence
