# Tasks: Implement OAPI Lark Provider

## 1. OpenSpec

- [x] 1.1 Create proposal, design, tasks, and delta specs.
- [x] 1.2 Validate `openspec validate implement-oapi-lark-provider`.

## 2. Provider Implementation

- [x] 2.1 Add `ProviderMode.OAPI`.
- [x] 2.2 Add `OapiHttpRunner` using standard-library HTTP.
- [x] 2.3 Add `OapiLarkProvider` behind `LarkToolAdapter`.
- [x] 2.4 Map existing read and write operations to OAPI request specs.
- [x] 2.5 Preserve dry-run behavior for write operations without network calls.

## 3. Entrypoints

- [x] 3.1 Allow `provider_mode="oapi"` in meeting schemas and tool parameters.
- [x] 3.2 Route workflow adapter creation to `LarkToolAdapter.oapi`.

## 4. Tests and Validation

- [x] 4.1 Add fake HTTP-runner tests for request mapping and token header behavior.
- [x] 4.2 Add tests that write dry-run does not call HTTP.
- [x] 4.3 Add tests that unapproved OAPI writes are rejected by `LarkToolAdapter`.
- [x] 4.4 Run `uv run python -m pytest tests/meeting -q`.
- [x] 4.5 Run `uv run ruff check nanobot tests`.
- [x] 4.6 Run `openspec validate implement-oapi-lark-provider`.
- [x] 4.7 Update OAPI provider docs and production env notes.
