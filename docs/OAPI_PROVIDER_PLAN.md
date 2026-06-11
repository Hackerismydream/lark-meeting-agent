# OapiLarkProvider Status

`CliLarkProvider` is useful for local real smoke and diagnostics. Production Feishu bot deployment now has an OpenAPI-backed provider boundary behind `LarkToolAdapter`.

## Provider Roles

```text
FakeLarkProvider
  -> CI, deterministic tests, no credentials.

CliLarkProvider
  -> local demos, real smoke, troubleshooting.

OapiLarkProvider
  -> production bot target and direct OpenAPI request boundary.
```

All providers must remain behind `LarkToolAdapter`.

## Implemented Operations

The MVP provider maps only operations needed for the bot:

- `auth.status` or equivalent credential health check,
- `vc.search` or minutes search,
- `vc.notes` or equivalent minutes/transcript fetch,
- `docs.create`,
- `task.create`,
- `im.send`.

Write operations support `dry_run=True` previews without sending HTTP. Real writes still require `LarkToolAdapter` approval.

## Token and Identity Model

The current provider accepts an already-issued access token through constructor injection or `LARK_OAPI_ACCESS_TOKEN`.

Provider errors are classified as:

- `invalid_token`
- `missing_scope`
- `permission_denied`
- `rate_limit`
- `unavailable`

Still-open production work:

- app ID and app secret,
- tenant access token,
- user access token if user-owned reads are required,
- bot identity for sends,
- token refresh and expiry,
- tenant permissions and scopes,
- redaction in logs/traces/audit.

## Implementation Rules

- No workflow calls Lark HTTP APIs or SDKs directly.
- Adapter operation names remain stable.
- Fake tests do not require real credentials.
- Real tests are opt-in.
- Write operations remain approval-gated.
- Production docs must state which identity performs each read/write.

## Current Status

Implemented as a standard-library HTTP provider in `nanobot/meeting/lark_oapi_provider.py` with fake-runner tests, schema validation, dry-run write previews, approval gating through `LarkToolAdapter`, and classified provider errors. Real Feishu app deployment, token refresh, scope verification, and end-to-end OpenAPI smoke remain pending. Until those are verified, this is an OpenAPI provider boundary, not a production deployment claim.
