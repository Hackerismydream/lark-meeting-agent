# Api Spec Delta for Phase 2: Agent Companion API

## ADDED Requirements

### Requirement: Phase 2: Agent Companion API Api Contract

The system MUST satisfy the api contract for this V1.1 phase.

#### Scenario: Phase artifact exists

- GIVEN this phase is implemented
- WHEN a reviewer inspects the repository
- THEN the expected files and docs for `agent-companion-api` exist
- AND the implementation does not bypass backend approval or LarkToolAdapter boundaries.

#### Scenario: No direct Lark write from macOS

- GIVEN the macOS app needs to approve a write operation
- WHEN the user approves selected operation IDs
- THEN the app sends an approval request to the backend companion API
- AND does not call Lark APIs directly.
