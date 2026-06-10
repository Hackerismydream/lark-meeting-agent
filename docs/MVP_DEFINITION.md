# MVP Definition

Lark Meeting Agent MVP is a lifecycle meeting workflow agent built inside HKUDS/nanobot v0.2.1. Its primary real acquisition path is a visible, approval-gated live meeting listener that joins an in-progress Feishu/Lark meeting and ingests meeting events. It also processes transcript fixtures or optional historical minutes, generates structured meeting intelligence with evidence, prepares approval-gated Lark write operations, persists meeting knowledge, and answers questions with sources.

## Required Scenarios

### Fake CI Vertical Slice

```text
transcript fixture
-> TranscriptNormalizer
-> FakeMeetingAnalyzer
-> MeetingMinutes with evidence
-> WritePlan
-> fake approval
-> FakeLarkProvider execution
-> local meeting memory
-> QA with sources
```

This scenario must pass without Lark credentials or LLM keys.

### Real Live Listener Gate

```text
approved visible bot join
-> lark-cli vc +meeting-join
-> lark-cli vc +meeting-events
-> LiveLarkMeetingWorkflow event conversion
-> LiveMeetingWorkflow state and QA
-> approved visible bot leave
```

This scenario is local/manual and uses `scripts/lma-real`.

### Optional Historical Read + Real LLM Dry-run

```text
lark-cli vc search
-> fetch transcript/minutes text
-> real LLM analyzer
-> Pydantic validation
-> WritePlan
-> no writes executed
```

This scenario is local/manual and uses `scripts/lma-real`. It depends on the authorized account having readable historical notes/minutes and is not the primary product gate.

### Approval-gated Real Writes

```text
approve selected operation ids
-> docs.create/task.create/optional im.send through LarkToolAdapter
-> audit events
-> persisted operation results
```

No write happens during `process`.

### nanobot Entrypoint

```text
lark_meeting(action="process")
lark_meeting(action="approve")
lark_meeting(action="qa")
lark_meeting(action="status")
lark_meeting(action="live_join")
lark_meeting(action="live_poll")
lark_meeting(action="live_leave")
```

The tool calls deterministic meeting workflows and never calls `lark-cli` directly.

### Cross-meeting QA With Sources

```text
persisted meeting memory
-> keyword/structured retrieval
-> answer with meeting_id + segment_id sources
```

If no evidence is found, the system reports insufficient evidence.

## Non-goals

- Custom ASR.
- Invisible realtime meeting capture.
- Unapproved live meeting join/leave.
- Pre-brief workflow.
- Vector database.
- Complex frontend.
- Independent Feishu bot runtime.
- Independent agent runtime.
