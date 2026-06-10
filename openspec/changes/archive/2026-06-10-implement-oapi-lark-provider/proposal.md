# Change: Implement OAPI Lark Provider

## Summary

Add an `OapiLarkProvider` behind `LarkToolAdapter` so production deployments can use Lark OpenAPI directly instead of depending only on `lark-cli`.

## Motivation

The current system supports fake provider tests and CLI-based real diagnostics. The main provider spec now requires the system to distinguish fake, CLI, and OpenAPI provider roles. Production bot readiness needs an OpenAPI provider boundary that preserves allowlists, approval gating, dry-run semantics, audit redaction, and credential-free tests.

## Scope

- Add `ProviderMode.OAPI`.
- Add `OapiLarkProvider` using standard-library HTTP.
- Keep all OAPI calls behind `LarkToolAdapter`.
- Map existing allowlisted read/write operations to endpoint specs.
- Make write dry-runs return previews without network calls.
- Add fake HTTP-runner unit tests.
- Do not require real Lark credentials in CI.

## Non-goals

- No production OAuth onboarding UI.
- No tenant-token lifecycle daemon.
- No real Feishu app deployment claim.
- No widening of the write allowlist.
- No direct workflow access to HTTP APIs.
