## 1. OpenSpec

- [x] 1.1 Add live listener proposal, design, tasks, and delta specs.
- [x] 1.2 Validate `openspec validate pivot-live-meeting-listener`.

## 2. Adapter Contract

- [x] 2.1 Add fake provider support for `vc.meeting.join`, `vc.meeting.events`, and `vc.meeting.leave`.
- [x] 2.2 Add CLI provider argv mapping for `+meeting-join`, `+meeting-events`, and `+meeting-leave`.
- [x] 2.3 Add OAPI request mapping for bot join, events, and leave.
- [x] 2.4 Keep join/leave approval-gated and audited.

## 3. Live Lark Workflow

- [x] 3.1 Add a live Lark workflow that starts a local live run from a join result.
- [x] 3.2 Convert Lark raw events into `LiveMeetingEvent` objects.
- [x] 3.3 Poll live events and ingest transcript deltas into `LiveMeetingWorkflow`.
- [x] 3.4 Persist page tokens and return source-grounded live state.

## 4. Entrypoints and Docs

- [x] 4.1 Add CLI commands for `live-join`, `live-poll`, and `live-leave`.
- [x] 4.2 Wire the commands into `scripts/lma-real`.
- [x] 4.3 Update product/blocker docs to make live listening the primary real path.
- [x] 4.4 Add a live listener runbook with fake and real smoke commands.

## 5. Verification

- [x] 5.1 Add failing tests first for adapter and workflow behavior, then implement.
- [x] 5.2 Run `pytest tests/meeting -q`.
- [x] 5.3 Run `ruff check nanobot tests`.
- [x] 5.4 Commit and push the pivot as a reviewable unit.
