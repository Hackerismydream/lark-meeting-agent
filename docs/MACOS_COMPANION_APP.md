# macOS Companion App

V1.1 adds a macOS companion client for Lark Meeting Agent.

The macOS app is not a second Agent runtime. It controls and observes the existing backend Agent Service through a Companion API. Lark reads and writes remain backend responsibilities, and all writes still pass through backend approval policy and `LarkToolAdapter`.

## Product Boundary

The app may:

- show Agent connection status,
- show today's meetings when the backend provides them,
- request pre-brief generation,
- list pending WritePlans,
- approve or reject selected operation IDs,
- show run status and run traces,
- search meeting memory,
- upload `.txt`, `.md`, or `.json` transcript files for backend processing,
- open Feishu result links returned by the backend.

The app must not:

- call Lark APIs directly,
- execute `lark-cli`,
- implement an autonomous Agent loop in Swift,
- approve writes without showing `run_id` and operation IDs,
- store bearer tokens in plain text,
- claim ASR/audio transcription support in V1.1.

## Connection Modes

Local mode connects to a local Agent Service, for example:

```text
http://127.0.0.1:8765
```

Remote mode connects to a deployed Agent Service and must require a bearer token.

Persisted bearer tokens must use Keychain Services. Non-sensitive settings such as API base URL, environment label, and notification preferences may use app settings storage.

## Companion API Contract

The backend Companion API is a thin adapter over existing workflows and repositories.

```text
GET  /v1/agent/status
GET  /v1/meetings/today
POST /v1/prebrief
GET  /v1/runs
GET  /v1/runs/{run_id}
GET  /v1/runs/{run_id}/trace
GET  /v1/write-plans/pending
POST /v1/runs/{run_id}/approve
POST /v1/runs/{run_id}/reject
POST /v1/search
POST /v1/upload/transcript
```

All responses should use a typed envelope:

```json
{
  "ok": true,
  "data": {},
  "error": null
}
```

Errors should use:

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "permission",
    "message": "safe user-facing message"
  }
}
```

## Approval UX Contract

The approval inbox must show:

- `run_id`,
- operation IDs,
- operation type,
- target,
- preview,
- risk or warning if present,
- backend status.

The app may approve selected operation IDs only by calling:

```text
POST /v1/runs/{run_id}/approve
```

The request must include explicit `operation_ids`. A vague "approve all" action is not allowed unless the UI first displays the full operation list and submits explicit IDs.

## Security Model

- Tokens are stored in Keychain or not persisted.
- Tokens must not be logged.
- Production backend connections must display a warning.
- Backend stale-run, provider-mismatch, already-completed, rejected, or permission errors must be displayed and must not trigger silent retry.
- The app does not bypass backend access policy.

## Implementation Status

The backend Companion API adapter is implemented in `nanobot/meeting/companion_api.py` with typed models in `nanobot/meeting/companion_models.py`. It is an in-process adapter that can be mounted by a future HTTP layer.

The Phase 3 macOS shell is implemented in `apps/macos/LarkMeetingAgent`.

Current shell capabilities:

- Swift Package with `LarkMeetingAgent` executable target.
- SwiftUI `MenuBarExtra` entry for Agent status.
- Settings view for API base URL, environment label, and notification preference.
- API client for `GET /v1/agent/status`.
- Approval inbox for `GET /v1/write-plans/pending`.
- Selected-operation approval through `POST /v1/runs/{run_id}/approve`.
- Run rejection through `POST /v1/runs/{run_id}/reject`.
- Local macOS notifications for pending approvals when enabled.
- Today meeting list from `GET /v1/meetings/today`.
- Pre-brief generation through `POST /v1/prebrief`.
- Run status and trace inspection through `GET /v1/runs`, `GET /v1/runs/{run_id}`, and `GET /v1/runs/{run_id}/trace`.
- Cross-meeting source-grounded search through `POST /v1/search`.
- Local text transcript upload through `POST /v1/upload/transcript` for `.txt`, `.md`, and `.json`.
- Bearer token injection from a credential store.
- Keychain-backed credential store plus in-memory test store.
- Core smoke runner covering status decode, bearer token header injection, and credential round trip.

Deferred to later V1.1 phases:

- packaging, signing, and notarization docs.

## Phase 3 Validation

Validated on this workstation:

```bash
swift build --package-path apps/macos/LarkMeetingAgent
swift run --package-path apps/macos/LarkMeetingAgent LarkMeetingAgentCoreSmokeTests
uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py
openspec validate macos-app-shell-status
```

`swift test --package-path apps/macos/LarkMeetingAgent` is intentionally not the Phase 3 Swift gate on this machine because the active Command Line Tools SwiftPM environment does not provide XCTest or Swift Testing modules. The package therefore uses an executable smoke runner until a full Xcode test runtime is available.

`xcodebuild` is blocked on this workstation because `xcode-select` points to CommandLineTools rather than a full Xcode installation.
