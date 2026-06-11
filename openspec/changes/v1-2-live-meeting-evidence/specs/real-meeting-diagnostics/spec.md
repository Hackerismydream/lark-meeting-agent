## ADDED Requirements

### Requirement: Real meeting blocker classification

The runner SHALL classify common real meeting failures.

#### Scenario: Permission blocker

- **WHEN** Lark returns no-permission or permission errors
- **THEN** the runner SHALL classify the failure as `permission`
- **AND** it SHALL record the next action without leaking tokens or secrets

#### Scenario: No events blocker

- **WHEN** join succeeds but no event is returned
- **THEN** the runner SHALL classify the failure as `no_events`
