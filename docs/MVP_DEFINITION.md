# MVP Definition

Lark Meeting Agent MVP is a post-meeting workflow agent built inside HKUDS/nanobot v0.2.1. It processes completed Feishu/Lark meetings or transcript fixtures, generates structured meeting minutes with evidence, prepares approval-gated Lark write operations, persists meeting knowledge, and answers cross-meeting questions with sources.

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

### Real Lark Read + Real LLM Dry-run

```text
lark-cli vc search
-> fetch transcript/minutes text
-> real LLM analyzer
-> Pydantic validation
-> WritePlan
-> no writes executed
```

This scenario is local/manual and uses `scripts/lma-real`.

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
- Realtime meeting bot.
- Joining live meetings.
- Pre-brief workflow.
- Vector database.
- Complex frontend.
- Independent Feishu bot runtime.
- Independent agent runtime.
