# Design: Real Transcript Gate Helper

## Context

`docs/BLOCKERS.md` documents the current real-data blocker: `lark-cli` auth works and meetings are visible, but visible meetings currently have no readable notes/minutes transcript. The remaining MVP gates should not require manual interpretation of raw `lark-cli` output.

## Design

Add `TranscriptGateWorkflow`.

```text
scripts/lma-real transcript-gate
  -> nanobot.meeting.cli transcript-gate
  -> TranscriptGateWorkflow
  -> LarkToolAdapter
      -> fake provider in tests
      -> cli/oapi provider in real runs
```

The workflow performs read-only operations:

1. `auth.status`
2. `vc.search`
3. `vc.notes` for visible meetings
4. `minutes.search`

It returns:

- `status`: `ready` or `blocked`,
- provider mode,
- query/time range,
- visible meeting count,
- accessible minute count,
- first readable source if found,
- checked meeting attempts with blocker reasons,
- next process command if ready,
- blocker message if blocked.

## Safety

- The helper never calls write operations.
- It does not run the LLM.
- It does not create docs, tasks, or messages.
- Tests use fake provider behavior and do not require real Lark credentials.
