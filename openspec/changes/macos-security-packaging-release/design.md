# Design: Phase 7: macOS Security, Packaging, and Release

## Architecture Principle

The macOS app is a companion client. It must communicate with the Agent Service / Companion API and must not directly call Lark APIs or execute write operations.

## Key Design Points

- Keychain token storage.
- No token logs.
- Production environment warning.
- Manual QA checklist.
- Packaging docs.
- Signing/notarization docs but do not claim completed unless actually done.

## Required Artifacts

- `docs/MACOS_SECURITY.md`
- `docs/MACOS_PACKAGING.md`
- `docs/MACOS_MANUAL_QA.md`
- `docs/MACOS_ENVIRONMENT.md`
- OpenSpec change files

## Validation

`swift test` if available
`xcodebuild ... build` if available
`openspec validate macos-security-packaging-release`
