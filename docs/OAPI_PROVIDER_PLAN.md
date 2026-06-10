# OapiLarkProvider Plan

`CliLarkProvider` is useful for local real smoke and diagnostics, but production Feishu bot deployment should move toward an OpenAPI-backed provider.

## Provider Roles

```text
FakeLarkProvider
  -> CI, deterministic tests, no credentials.

CliLarkProvider
  -> local demos, real smoke, troubleshooting.

OapiLarkProvider
  -> production bot target.
```

All providers must remain behind `LarkToolAdapter`.

## Target Operations

Production MVP should implement only operations needed for the bot:

- `auth.status` or equivalent credential health check,
- `vc.search` or minutes search,
- `vc.notes` or equivalent minutes/transcript fetch,
- `docs.create`,
- `task.create`,
- `im.send`.

## Token and Identity Model

The provider design must explicitly handle:

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

Not implemented. Until this provider exists, the production bot track is architecture/spec and local diagnostic execution remains based on `CliLarkProvider`.
