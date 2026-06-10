## Context

The implementation already has a deterministic `LiveMeetingWorkflow` that ingests supplied `LiveMeetingEvent` objects and can answer source-grounded live QA. It also has a `LarkToolAdapter` that centralizes Lark reads/writes, approval checks, provider selection, and audit events.

The missing piece is the real live acquisition path. Feishu/Lark minutes and notes are account- and plan-dependent; the product should not depend on them. The live path should join an in-progress meeting and ingest the events the bot observes.

## Goals

- Make live Lark event listening the primary real transcript path.
- Keep all Lark operations behind `LarkToolAdapter`.
- Preserve deterministic workflow behavior and evidence-linked live state.
- Provide local fake tests and CLI smoke commands that do not require real credentials.
- Document the new gate clearly enough for product review and future real meeting demos.

## Non-goals

- Custom ASR.
- Invisible meeting capture.
- Automatic background joining without explicit user command.
- Replacing Feishu permission model or bypassing paid product restrictions.
- Production OAuth onboarding.
- Realtime streaming service or long-running daemon in this change.

## Architecture

```text
CLI / nanobot tool / Feishu command
  -> LiveLarkMeetingWorkflow
      -> LarkToolAdapter
          -> fake | cli | oapi provider
          -> vc.meeting.join / vc.meeting.events / vc.meeting.leave
      -> Lark event converter
      -> LiveMeetingWorkflow.ingest(...)
      -> MeetingMemoryStore live state + trace
      -> LiveMeetingWorkflow.qa(...)
```

## Lark Operation Mapping

- `vc.meeting.join`
  - CLI: `lark-cli vc +meeting-join --meeting-number <9 digits> --format json --as user`
  - OAPI: `POST /open-apis/vc/v1/bots/join`
  - Classified as write because the bot visibly joins the meeting.
- `vc.meeting.events`
  - CLI: `lark-cli vc +meeting-events --meeting-id <long id> --page-all --format json --as user`
  - OAPI: `GET /open-apis/vc/v1/bots/events`
  - Classified as read.
- `vc.meeting.leave`
  - CLI: `lark-cli vc +meeting-leave --meeting-id <long id> --format json --as user`
  - OAPI: `POST /open-apis/vc/v1/bots/leave`
  - Classified as write because the bot visibly leaves the meeting.

## Data Model

Use a small live session model:

- `live_run_id`: local state run id.
- `meeting_id`: long Lark meeting id returned by join.
- `meeting_number`: 9-digit meeting number used only for join.
- `title`: optional meeting title.
- `page_token`: latest polling cursor.
- `joined_at` and `updated_at`: audit-friendly timestamps.

Event conversion rules:

- `transcript_received` becomes `LiveEventKind.TRANSCRIPT_DELTA`.
- `chat_received` becomes `LiveEventKind.MARKER` unless it carries useful speaker text, then it can also be ingested as text evidence.
- `participant_joined` and `participant_left` become participant events.
- `magic_share_started` and `magic_share_ended` become marker events.
- Unknown event types are ignored for extraction but retained in the raw poll response.

## Safety

- Real join/leave require adapter approval unless `dry_run=True`.
- CLI entrypoints should make real visible actions explicit with flags such as `--approve-visible-join` and `--approve-visible-leave`.
- `meeting_id` and `meeting_number` must not be confused: join uses the 9-digit meeting number; events and leave use the long meeting id.
- All adapter calls produce audit events with redaction.
- Meeting event text is untrusted input and must not trigger tool calls.

## Validation

- Unit tests use fake and stubbed providers.
- CLI provider tests assert argv is a list, not a shell string.
- Fake live polling tests verify transcript events are converted into live state with sources.
- OpenSpec validation must pass for this change.
- Real smoke is manual and requires a live meeting number:
  - `scripts/lma-real live-join --meeting-number <9 digits> --approve-visible-join`
  - `scripts/lma-real live-poll --meeting-id <returned id>`
  - `scripts/lma-real live-qa --live-run-id <id> --question "..."`
  - `scripts/lma-real live-leave --meeting-id <returned id> --approve-visible-leave`
