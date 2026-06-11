# Design: Phase 3: macOS App Shell and Menu Bar Status

## Architecture Principle

The macOS app is a companion client. It must communicate with the Agent Service / Companion API and must not directly call Lark APIs or execute write operations.

## Key Design Points

- Use SwiftUI.
- Use MenuBarExtra where available.
- API client talks to companion API.
- Settings store API URL in UserDefaults, token in Keychain.
- Support connected/disconnected/pending count status.

## Required Artifacts

- `apps/macos/LarkMeetingAgent/`
- `Package.swift` or Xcode project
- Swift models and API client
- Settings view
- Status view
- Tests if Swift test environment available
- OpenSpec change files

## Validation

`swift test` if available
`xcodebuild ... build` if available
`openspec validate macos-app-shell-status`
