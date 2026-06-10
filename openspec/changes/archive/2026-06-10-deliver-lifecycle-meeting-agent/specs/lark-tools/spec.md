## ADDED Requirements

### Requirement: Lifecycle Lark Read Operations
`LarkToolAdapter` MUST allow controlled read operations for calendar agenda, meeting search, meeting notes, minutes search, document fetch/search, and task lookup.

#### Scenario: Calendar agenda read
- **WHEN** a pre-brief requires upcoming meeting context
- **THEN** the workflow calls `LarkToolAdapter` with `calendar.agenda` and receives typed agenda data.

### Requirement: Adapter Retry and Timeout
The CLI provider MUST support bounded timeout and retry behavior for transient read failures.

#### Scenario: Transient read failure
- **WHEN** a read operation fails with a retryable CLI error
- **THEN** the provider retries up to the configured limit and records attempts in audit.

### Requirement: Lifecycle Write Allowlist
Write operations MUST remain limited to docs, tasks, and IM messages unless a later spec expands the write set.

#### Scenario: Calendar write rejected
- **WHEN** a workflow attempts `calendar.create`
- **THEN** the adapter rejects it as not allowlisted.
