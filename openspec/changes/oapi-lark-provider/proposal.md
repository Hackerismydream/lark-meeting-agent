# Proposal: Production Lark OpenAPI Provider

## Intent

Implement V1.0 phase `oapi-lark-provider` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Preserve LarkToolAdapter interface.
- Add OapiLarkProvider for production path.
- Support minimal operations: auth/status equivalent, calendar.agenda or minutes/vc search, docs.create, task.create, im.send where feasible.
- Real tests opt-in only.
- HTTP/API tests may use fake responses or recorded sanitized fixtures.

## Scope

This change covers:

- Preserve LarkToolAdapter interface.
- Add OapiLarkProvider for production path.
- Support minimal operations: auth/status equivalent, calendar.agenda or minutes/vc search, docs.create, task.create, im.send where feasible.
- Real tests opt-in only.
- HTTP/API tests may use fake responses or recorded sanitized fixtures.
- Token and secret redaction required.
- Provider errors classified: missing scope, invalid token, permission denied, rate limit, unavailable.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- Fake tests pass without Lark credentials.
- CliLarkProvider still works.
- Oapi provider operations schema-validated.
- No writes without approval.
- Docs explain which operations are implemented vs planned.
