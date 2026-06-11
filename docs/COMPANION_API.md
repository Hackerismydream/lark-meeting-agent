# Companion API

The Companion API is a thin backend adapter for the macOS app. It wraps existing meeting workflows and repositories; it is not a new Agent runtime.

## Auth

Local development may run without a token. Any remote or production-like mode must require a bearer token.

The macOS app must store persisted tokens in Keychain.

## Response Envelope

Success:

```json
{
  "ok": true,
  "data": {},
  "error": null
}
```

Failure:

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

## Routes

- `GET /v1/agent/status`
- `GET /v1/meetings/today`
- `POST /v1/prebrief`
- `GET /v1/runs`
- `GET /v1/runs/{run_id}`
- `GET /v1/runs/{run_id}/trace`
- `GET /v1/write-plans/pending`
- `POST /v1/runs/{run_id}/approve`
- `POST /v1/runs/{run_id}/reject`
- `POST /v1/search`
- `POST /v1/upload/transcript`

## Write Safety

Approval requests must include explicit operation IDs. The API delegates approval/rejection to the existing backend policy and workflows. It does not call Lark APIs directly.

Transcript upload accepts `.txt`, `.md`, and `.json` text files only. V1.1 does not implement ASR.
