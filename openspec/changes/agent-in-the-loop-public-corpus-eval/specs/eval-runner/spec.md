## ADDED Requirements

### Requirement: Eval runner modes

The eval runner SHALL support `mode=mock_smoke` and `mode=agent`.

#### Scenario: Mock smoke remains available

- **WHEN** the runner is invoked with `mode=mock_smoke`
- **THEN** it SHALL use the existing fixture-to-mock-tools flow
- **AND** it SHALL NOT call real Lark APIs

#### Scenario: Agent mode invokes workflows

- **WHEN** the runner is invoked with `mode=agent`
- **THEN** it SHALL route fixtures through Agent workflows
- **AND** it SHALL write report, trace, predictions, failures, and artifacts
