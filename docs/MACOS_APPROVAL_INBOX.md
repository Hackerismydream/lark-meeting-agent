# macOS Approval Inbox

Phase 4 adds a menu bar approval inbox for pending backend WritePlans.

The macOS app does not execute Lark writes. It displays backend-provided operations and sends explicit approval or rejection requests to the Companion API. The backend remains responsible for approval policy, stale-run checks, LarkToolAdapter execution, and audit logging.

## User Flow

1. The app calls `GET /v1/write-plans/pending`.
2. Pending runs are grouped by `run_id`.
3. Each operation shows:
   - operation ID,
   - operation type,
   - preview,
   - target summary,
   - approval status,
   - execution status.
4. The user selects one or more operations in a specific run.
5. The app calls `POST /v1/runs/{run_id}/approve` with explicit `operation_ids`.
6. The app refreshes pending approvals from the backend.

Rejecting a run calls `POST /v1/runs/{run_id}/reject`.

## Safety Rules

- There is no vague approve-all button.
- Approval buttons are disabled until at least one operation is selected.
- Operation selection is scoped by both `run_id` and `operation_id` because operation IDs may repeat across runs.
- Bearer tokens are loaded through the credential store and are not logged.
- The app never calls Lark APIs, `lark-cli`, or backend-internal Lark providers.
- Backend errors are displayed as user-facing failure messages and do not trigger silent retries.

## Notifications

If notifications are enabled in settings, the app can request macOS local notification permission and schedule a local notification when pending approvals are present.

Notifications are local only. V1.1 does not require remote push notifications.

## Validation

Validated on this workstation:

```bash
swift build --package-path apps/macos/LarkMeetingAgent
swift run --package-path apps/macos/LarkMeetingAgent LarkMeetingAgentCoreSmokeTests
uv run python -m pytest tests/meeting -q
openspec validate macos-approval-inbox-notifications
```

The active Command Line Tools SwiftPM environment has no usable XCTest or Swift Testing module, so the repository uses `LarkMeetingAgentCoreSmokeTests` as the Phase 4 Swift validation runner.
