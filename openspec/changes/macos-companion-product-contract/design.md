# Design: Phase 1: macOS Product Contract and Agent API Contract

## Architecture Principle

The macOS app is a companion client. It must communicate with the Agent Service / Companion API and must not directly call Lark APIs or execute write operations.

## Key Design Points

- macOS app is a companion client, not primary runtime.
- App never writes to Lark directly.
- Backend API is a thin adapter over existing workflows.
- Keychain is required for persisted tokens.
- Approval UX must display run_id and operation IDs.

## Required Artifacts

- `openspec/changes/macos-companion-product-contract/proposal.md`
- `design.md`
- `tasks.md`
- `specs/product/spec.md`
- `specs/api/spec.md`
- `specs/security/spec.md`
- `docs/MACOS_COMPANION_APP.md`

## Validation

`openspec validate macos-companion-product-contract`
