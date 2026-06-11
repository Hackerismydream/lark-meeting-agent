# Security Spec Delta for Phase 5: PreBrief, Meeting Timeline, and Run Trace Viewer

## ADDED Requirements

### Requirement: Phase 5: PreBrief, Meeting Timeline, and Run Trace Viewer Security Contract

The system MUST satisfy the security contract for this V1.1 phase.

#### Scenario: Phase artifact exists

- GIVEN this phase is implemented
- WHEN a reviewer inspects the repository
- THEN the expected files and docs for `macos-prebrief-trace-viewer` exist
- AND the implementation does not bypass backend approval or LarkToolAdapter boundaries.

#### Scenario: No direct Lark write from macOS

- GIVEN the macOS app needs to approve a write operation
- WHEN the user approves selected operation IDs
- THEN the app sends an approval request to the backend companion API
- AND does not call Lark APIs directly.
