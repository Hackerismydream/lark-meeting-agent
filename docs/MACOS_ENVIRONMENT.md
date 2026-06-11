# macOS Environment

The macOS companion app connects to a backend Agent Service through the Companion API.

## Local Development

Recommended local API base URL:

```text
http://127.0.0.1:8765
```

Local development may run without a bearer token only when the backend Companion API is explicitly configured that way.

## Remote or Production Backend

Remote and production backends must require bearer authentication.

The app stores:

- API base URL in `UserDefaults`,
- environment label in `UserDefaults`,
- notification preference in `UserDefaults`,
- bearer token in Keychain.

The environment label is display and warning metadata. It is not an authorization boundary. Backend policy remains authoritative.

## Backend Requirements

The backend should expose:

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

All backend writes must still require backend approval and execute through `LarkToolAdapter`.
