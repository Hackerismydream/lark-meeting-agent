# Design: V1.2 Live Meeting Evidence

## Version Definition

V1.2 is a live meeting evidence loop:

```text
explicit visible join approval
-> dry-run join preview
-> real join
-> event poll
-> live state update
-> live QA
-> explicit visible leave
-> evidence pack / blocker
```

## Reference Project Integration

`lark-meeting-talk-agent` contributes ideas, not code:

- always-on meeting memory,
- explicit state machine,
- low-friction single-process runtime,
- current-meeting-scoped event/artifact enrichment,
- clear lifecycle cleanup.

We do not import its ASR/TTS/Realtime WebSocket stack in V1.2.

## Evidence Pack

The runner writes:

```text
runs/live_real/<meeting_number>/
  report.json
  blocker.md
  join_dry_run.json
  live_smoke_result.json
  raw_event_shapes.json
  audit.jsonl
```

If join fails, the pack still contains dry-run request shape and a diagnosis.

## Safety

Join and leave remain visible write operations and require explicit approval flags. The runner never auto-approves, never writes docs/tasks/messages, and redacts raw provider output.
