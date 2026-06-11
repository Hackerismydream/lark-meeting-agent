# Deployment Spec Delta for Phase 6: Cross-meeting Search and Local Transcript Upload

## ADDED Requirements

### Requirement: Phase 6: Cross-meeting Search and Local Transcript Upload Deployment Contract

The system MUST satisfy the deployment contract for this V1.1 phase.

#### Scenario: Phase artifact exists

- GIVEN this phase is implemented
- WHEN a reviewer inspects the repository
- THEN the expected files and docs for `macos-search-upload` exist
- AND the implementation does not bypass backend approval or LarkToolAdapter boundaries.

#### Scenario: No direct Lark write from macOS

- GIVEN the macOS app needs to approve a write operation
- WHEN the user approves selected operation IDs
- THEN the app sends an approval request to the backend companion API
- AND does not call Lark APIs directly.
