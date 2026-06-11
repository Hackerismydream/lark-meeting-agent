# Design: Phase 4: Approval Inbox and Notifications

## Architecture Principle

The macOS app is a companion client. It must communicate with the Agent Service / Companion API and must not directly call Lark APIs or execute write operations.

## Key Design Points

- Fetch pending WritePlans.
- Show operations with preview/target/risk.
- Approve selected operation IDs.
- Reject run.
- Use UserNotifications for local notifications if macOS environment supports it.

## Required Artifacts

- ApprovalInbox view
- WriteOperation detail view
- Notification service
- ViewModel tests
- `docs/MACOS_APPROVAL_INBOX.md`
- OpenSpec change files

## Validation

`swift test` if available
`uv run python -m pytest tests/meeting -q`
`openspec validate macos-approval-inbox-notifications`
