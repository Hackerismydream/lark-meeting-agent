## ADDED Requirements

### Requirement: Evidence redaction

Lark outputs written to evidence packs SHALL be sanitized.

#### Scenario: Sensitive values are redacted

- **WHEN** evidence contains token, secret, cookie, authorization, user id, open id, email, phone, or chat id fields
- **THEN** the stored evidence SHALL replace those values with `[REDACTED]`
