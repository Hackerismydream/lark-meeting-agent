# Proposal: Local Transcript Live Session

## Summary

Implement the first V2.0 local meeting capture step: a user-initiated local transcript live session over an append-only transcript file.

## Motivation

Feishu official live bot join remains supported, but it is blocked in the current environment by external permission / gray release. V2.0 must keep product development moving by supporting local meeting input sources that feed the same live workflow and evidence model.

## Scope

- Harden input provider capabilities and typed errors.
- Add append-mode polling to `LocalTranscriptProvider`.
- Add a local listener runner that feeds provider events into `LiveMeetingWorkflow`.
- Add live QA over the local transcript session.
- Add optional post-meeting minutes and dry-run `WritePlan` generation from accumulated transcript.
- Add CLI entrypoint and documentation.
- Add tests.

## Non-goals

- No ScreenCaptureKit.
- No microphone capture.
- No ASR.
- No speaker diarization.
- No new macOS UI.
- No Feishu official provider removal.
- No real Lark calls.
- No Feishu writes.

## Validation

```bash
uv run python -m compileall nanobot/meeting
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate local-transcript-live-session
```

