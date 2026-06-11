# Design: Phase 6: Cross-meeting Search and Local Transcript Upload

## Architecture Principle

The macOS app is a companion client. It must communicate with the Agent Service / Companion API and must not directly call Lark APIs or execute write operations.

## Key Design Points

- Search query sends to backend.
- Answers display sources.
- Insufficient evidence state is visible.
- Transcript upload accepts txt/md/json.
- Upload creates run or returns typed error.

## Required Artifacts

- Search view
- Source citation view
- Upload view
- File picker integration
- API client methods
- Tests/mocks
- OpenSpec change files

## Validation

`swift test` if available
`openspec validate macos-search-upload`
