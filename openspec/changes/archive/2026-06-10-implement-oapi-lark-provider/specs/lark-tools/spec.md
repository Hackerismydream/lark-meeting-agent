## MODIFIED Requirements

### Requirement: Lifecycle Write Allowlist
Write operations MUST remain limited to docs, tasks, and IM messages unless a later spec expands the write set.

#### Scenario: OAPI write dry-run
- **WHEN** an OAPI write operation is requested with `dry_run=True`
- **THEN** the provider returns an HTTP request preview without sending the request.

#### Scenario: OAPI write requires approval
- **WHEN** an OAPI write operation is requested without adapter approval
- **THEN** the adapter rejects it before the provider sends HTTP.
