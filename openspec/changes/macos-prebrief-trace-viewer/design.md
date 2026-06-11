# Design: Phase 5: PreBrief, Meeting Timeline, and Run Trace Viewer

## Architecture Principle

The macOS app is a companion client. It must communicate with the Agent Service / Companion API and must not directly call Lark APIs or execute write operations.

## Key Design Points

- Show meeting list.
- Show pre-brief with sources.
- Show run detail and status.
- Show trace timeline.
- Show audit/write results.
- Show error categories.

## Required Artifacts

- Meetings view
- PreBrief view
- RunTrace view
- Trace models
- Mock fixtures
- OpenSpec change files

## Validation

`swift test` if available
`openspec validate macos-prebrief-trace-viewer`
