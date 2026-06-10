# Live Meeting Workflow Delta

## MODIFIED Requirements

### Requirement: Live Workflow Input Boundary
The live workflow MUST consume transcript/event streams supplied by fixtures, adapters, or the Lark live listener. It MUST NOT require custom ASR, paid meeting minutes, or direct VC control outside `LarkToolAdapter`.

#### Scenario: Lark event stream
- **WHEN** a Lark event stream is polled through `vc.meeting.events`
- **THEN** the workflow converts supported events into deterministic live meeting state.
- **AND** unsupported event types do not trigger tools or writes.
