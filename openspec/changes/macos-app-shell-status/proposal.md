# Proposal: Phase 3: macOS App Shell and Menu Bar Status

## Why

V1.1 moves macOS into a dedicated release after V1.0 production bot readiness.

This change supports the macOS companion app while preserving the backend Agent as the source of truth.

## What

Create the macOS app skeleton, SwiftUI menu bar entry, settings, connection status, and API client.

## Scope

- Use SwiftUI.
- Use MenuBarExtra where available.
- API client talks to companion API.
- Settings store API URL in UserDefaults, token in Keychain.
- Support connected/disconnected/pending count status.

## Non-goals

- No approval inbox yet.
- No notifications yet.
- No direct Lark calls.
- No App Store packaging yet.
