# Live Meeting Simulator

`nanobot/meeting/simulator.py` provides deterministic live meeting scenarios.

The simulator does not call Lark, LLMs, subprocesses, HTTP APIs, or SDKs. It only loads fixtures and emits Lark-like event pages.

## Supported Events

- `meeting_started`
- `participant_joined`
- `participant_left`
- `transcript_received`
- `chat_received`
- `magic_share_started`
- `magic_share_ended`
- `screen_share_started`
- `screen_share_ended`
- `topic_changed`
- `meeting_marker`
- `meeting_ended`
- malformed and unknown event shapes

## Pagination

`LiveMeetingSimulator.page(page_size=..., page_token=...)` returns:

- `events`
- `has_more`
- `page_token`
- `next_page_token`

Tokens use deterministic offsets and are intended for replay tests, not for compatibility with real Lark tokens.

## Replay

`LiveReplayEvaluator` uses the simulator to feed event pages into `LiveMeetingWorkflow`, deduplicates repeated event ids, ignores malformed text events, runs live QA cases, and produces deterministic metrics.
