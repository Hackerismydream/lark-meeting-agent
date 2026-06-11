# Local Transcript Live Session

This is the first V2.0 local meeting capture step.

It lets a user run a live meeting session from an explicit append-only local transcript file:

```text
append-only transcript file
-> LocalTranscriptProvider
-> LiveMeetingEvent transcript deltas
-> LiveMeetingWorkflow
-> live QA
-> optional post-meeting minutes / WritePlan dry-run
```

## What It Does

- Reads a user-provided transcript file.
- Polls only newly appended transcript lines.
- Converts new lines into canonical `LiveMeetingEvent` transcript deltas.
- Updates `LiveMeetingWorkflow` state.
- Supports live QA with evidence sources or insufficient evidence.
- Can finalize accumulated transcript into post-meeting minutes and a dry-run WritePlan.

## What It Does Not Do

- No ScreenCaptureKit.
- No microphone capture.
- No system-audio capture.
- No ASR.
- No speaker diarization.
- No hidden monitoring.
- No real Lark calls.
- No Feishu writes.

## Transcript Format

Plain text lines:

```text
[00:01] Alice: 决定先做本地监听。
[00:02] Bob: 我负责补充风险清单。
```

Each non-empty line becomes one stable transcript segment.

## CLI

Run one poll:

```bash
uv run python -m nanobot.meeting.cli \
  --workspace /Users/martinlos/lark-meeting-agent \
  local-transcript-live \
  --transcript-file /tmp/live-meeting.txt \
  --meeting-id local-demo-1 \
  --title "本地会议"
```

Run multiple polls while another process appends lines:

```bash
uv run python -m nanobot.meeting.cli \
  --workspace /Users/martinlos/lark-meeting-agent \
  local-transcript-live \
  --transcript-file /tmp/live-meeting.txt \
  --meeting-id local-demo-1 \
  --title "本地会议" \
  --polls 10 \
  --poll-interval-sec 2
```

Ask live QA:

```bash
uv run python -m nanobot.meeting.cli \
  --workspace /Users/martinlos/lark-meeting-agent \
  local-transcript-live \
  --transcript-file /tmp/live-meeting.txt \
  --meeting-id local-demo-1 \
  --question "目前有哪些结论和待办？"
```

Finalize into minutes and dry-run WritePlan:

```bash
uv run python -m nanobot.meeting.cli \
  --workspace /Users/martinlos/lark-meeting-agent \
  local-transcript-live \
  --transcript-file /tmp/live-meeting.txt \
  --meeting-id local-demo-1 \
  --title "本地会议" \
  --finalize
```

The WritePlan is generated locally with `provider_mode=fake`; real Feishu writes still require the existing approval path and `LarkToolAdapter`.

## Provider API

Use `LocalTranscriptLiveRunner` for programmatic control:

```python
from nanobot.meeting.local_listener import LocalTranscriptLiveRunner

runner = LocalTranscriptLiveRunner("/path/to/workspace")
session = runner.start(
    transcript_file="/tmp/live-meeting.txt",
    meeting_id="local-demo-1",
    title="本地会议",
)
poll = runner.poll(session)
answer = runner.qa(poll.session, "目前有哪些结论？")
stopped = runner.stop(poll.session)
result = runner.finalize(stopped)
```

