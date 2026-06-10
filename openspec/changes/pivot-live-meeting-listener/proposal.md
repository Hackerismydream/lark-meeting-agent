## Why

The current real-data gate depends on Feishu/Lark minutes or meeting notes being available to the authorized account. That conflicts with the product direction: Lark Meeting Agent should replace paid meeting-minutes style capabilities by joining an in-progress meeting and listening to live meeting events.

This change pivots the primary real path from "read completed minutes" to "join a live meeting, poll event/transcript deltas, and maintain source-grounded live meeting state." Historical notes/minutes remain optional enrichment, not the product's main gate.

## What Changes

- Add a controlled live meeting listener path backed by `lark-cli vc +meeting-join`, `+meeting-events`, and `+meeting-leave`.
- Treat live meeting event ingestion as the primary real transcript acquisition route.
- Keep `vc.notes` and `minutes.search` as optional post-meeting enrichment only.
- Extend `LarkToolAdapter` with allowlisted live VC operations while preserving dry-run, approval, and audit behavior.
- Convert Lark meeting events into existing `LiveMeetingWorkflow` transcript/chat/participant events.
- Add CLI and `scripts/lma-real` entrypoints for live join, poll, QA, and leave flows.
- Update docs so reviewers do not read the project as blocked by paid minutes availability.

## Capabilities

### New Capabilities

- `live-lark-listener`: Real Lark meeting listener behavior, including join, event polling, event conversion, live state persistence, live QA, and leave.

### Modified Capabilities

- `product`: Product positioning changes from minutes-dependent real gate to live listener as the primary path.
- `lark-tools`: Add live VC bot operations to the controlled adapter contract.
- `live-meeting-workflow`: Expand supplied-event live workflow into a Lark event ingestion workflow.
- `safety`: Clarify that live join and leave are visible write operations requiring explicit approval or dry-run.
- `deployment`: Replace the current real transcript gate with a live meeting listener gate.

## Impact

- Code: `nanobot/meeting/lark_adapter.py`, `nanobot/meeting/live.py`, `nanobot/meeting/cli.py`, `scripts/lma-real`, tests under `tests/meeting/`.
- Docs: product brief, blocker notes, real demo/runbook docs, and a new live listener runbook.
- External systems: real smoke tests require a currently running Lark/Feishu meeting number and user authorization for `vc:meeting.bot.join:write` and `vc:meeting.meetingevent:read`.
- Safety: no real bot join is attempted without an explicit meeting number and approval flag; tests continue to use fake providers.
