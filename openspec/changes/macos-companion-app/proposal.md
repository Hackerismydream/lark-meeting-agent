## Why

The project should eventually have a macOS companion app, but not before the production Feishu bot path is stable. The app should be a control surface for approvals, traces, search, uploads, and reminders rather than a second agent runtime.

This change records the macOS direction without starting implementation.

## What Changes

- Define macOS app as a companion client to the production Feishu bot service.
- Define first-version scope: menu bar status, approval inbox, run trace viewer, cross-meeting search, and Lark artifact links.
- Define non-goals: no direct Lark writes, no independent agent runtime, no production bot replacement.
- Add `docs/MACOS_APP_ROADMAP.md`.

## Capabilities

### New Capabilities

- `macos-companion`: macOS companion app product scope, security model, and roadmap.

### Modified Capabilities

- `product`: Clarify that macOS is Phase 2 companion UX after production bot foundations.

## Impact

- Documentation only.
- No SwiftUI app, API server, packaging, or local runtime is implemented in this change.
