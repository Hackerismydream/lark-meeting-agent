# Lark Tools Delta

## MODIFIED Requirements

### Requirement: Lifecycle Lark Read Operations
`LarkToolAdapter` MUST allow controlled read operations for calendar agenda, meeting search, meeting notes, minutes search, document fetch/search, task lookup, and live meeting event polling.

#### Scenario: Live meeting events read
- **WHEN** a live workflow needs current meeting events
- **THEN** the workflow calls `LarkToolAdapter` with `vc.meeting.events`.
- **AND** the adapter classifies the operation as read.

### Requirement: Lifecycle Write Allowlist
Write operations MUST remain allowlisted and approval-gated. The allowlist MUST include docs, tasks, IM messages, and visible live VC bot join/leave operations.

#### Scenario: Live join requires approval
- **WHEN** `vc.meeting.join` is requested with `dry_run=False` and no approval
- **THEN** the adapter rejects it before calling the provider.

#### Scenario: Live leave requires approval
- **WHEN** `vc.meeting.leave` is requested with `dry_run=False` and no approval
- **THEN** the adapter rejects it before calling the provider.
