# Lark Provider Strategy

All Lark operations go through `LarkToolAdapter`.

## Providers

`FakeLarkProvider` is the default test provider. It is deterministic and requires no credentials.

`CliLarkProvider` is the local diagnostic provider. It shells out only inside the adapter boundary and is useful for user-authorized `lark-cli` smoke tests.

`OapiLarkProvider` is the production target provider. It converts adapter operations into Feishu/Lark OpenAPI requests and uses an injected access token or `LARK_OAPI_ACCESS_TOKEN`.

## Operation Policy

Read operations can execute through the selected provider.

Write operations require `LarkToolAdapter` approval:

- `docs.create`
- `task.create`
- `im.send`
- `vc.meeting.join`
- `vc.meeting.leave`

Dry-run writes return request previews and do not call HTTP.

## Production Status

The OpenAPI provider is fake-tested and schema-validated. It is not yet real-smoke verified against a configured Feishu app. Production rollout must verify token identity, scopes, endpoint behavior, rate limits, and audit redaction before claiming deployment.
