# macOS Pre-Brief and Trace Viewer

Phase 5 adds read-oriented views for meetings, pre-briefs, run status, write results, and run traces.

The macOS app remains a companion client. It requests data from the backend Companion API and does not run its own Agent loop, call Lark APIs, or execute hidden writes.

## Views

### Meetings

The meetings view calls:

```text
GET /v1/meetings/today
```

It displays backend-provided meeting titles and times. If the backend has no calendar provider configured, the view shows the backend source status rather than fabricating meetings.

### Pre-Brief

The pre-brief view calls:

```text
POST /v1/prebrief
```

It displays the goal, sections, bullets, warnings, and source citations returned by the backend. Sources are shown with meeting ID, segment ID, speaker, and timestamp when present.

### Run Trace

The run trace viewer calls:

```text
GET /v1/runs
GET /v1/runs/{run_id}
GET /v1/runs/{run_id}/trace
```

It displays run status, errors, write operation approval/execution results, trace stages, trace messages, and trace event data. Trace data is treated as display-only diagnostic context.

## Safety

- The app does not display bearer tokens or secrets.
- Backend trace redaction remains the source of truth for sensitive data.
- Errors are shown as safe user-facing messages.
- Inspecting traces cannot trigger approval, write execution, Lark API calls, or `lark-cli`.
- This phase is not a production observability dashboard.

## Validation

Validated on this workstation:

```bash
swift build --package-path apps/macos/LarkMeetingAgent
swift run --package-path apps/macos/LarkMeetingAgent LarkMeetingAgentCoreSmokeTests
uv run python -m pytest tests/meeting -q
openspec validate macos-prebrief-trace-viewer
```

`swift test --package-path apps/macos/LarkMeetingAgent` is still blocked by the package's executable-smoke-test strategy on this Command Line Tools environment.
