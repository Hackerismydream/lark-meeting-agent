# macos-companion Specification

## Purpose
TBD - created by archiving change macos-companion-app. Update Purpose after archive.
## Requirements
### Requirement: Companion app role
The macOS app MUST be a companion client for the production bot service, not the primary meeting agent runtime.

#### Scenario: Approval action
- **WHEN** a user approves a WritePlan in the macOS app
- **THEN** the approval is sent to the backend service and executed through backend `LarkToolAdapter`.

### Requirement: First-version UX
The first version MUST focus on menu bar meeting status, pre-brief notifications, approval inbox, run trace viewer, cross-meeting search, upload entry, and links to Lark artifacts.

#### Scenario: Approval inbox
- **WHEN** pending WritePlan operations exist
- **THEN** the app displays them with run ID, operation IDs, preview, and approve/reject actions.

### Requirement: No direct Lark writes
The macOS app MUST NOT call Lark APIs, `lark-cli`, or Lark SDKs directly for writes.

#### Scenario: Create task
- **WHEN** a user approves task creation in the app
- **THEN** the app sends an approval request to the backend and does not create the task itself.

