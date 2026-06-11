# Proposal: Local Meeting Input Provider

## Summary

Add a provider-agnostic meeting input layer and implement the first local providers:

- `LocalTranscriptProvider`
- `LocalAudioFileProvider`

The Feishu official live listener remains supported, but it is no longer the only way to feed meeting content into the live workflow.

## Motivation

Feishu official live bot join is currently blocked by external Feishu permission / gray release. Product development should continue without depending on that external gate. The system needs a clean input-provider boundary so local meeting sources can feed the same `LiveMeetingEvent` / `TranscriptSegment` pipeline used by official live providers.

## Scope

- Provider abstraction for start / poll / stop.
- Canonical provider session, config, event batch, and status models.
- Local transcript file provider.
- Local audio file provider with optional transcript sidecar.
- Tests for provider contracts and privacy boundaries.
- OpenSpec requirements for local input, privacy, and evaluation.

## Non-goals

- No full macOS SwiftUI app.
- No ScreenCaptureKit live system-audio capture.
- No microphone live streaming.
- No speaker diarization.
- No custom ASR implementation.
- No hidden monitoring.
- No changes to Feishu output / writeback workflows.
- No removal of Feishu official live provider.

## Validation

```bash
uv run python -m compileall nanobot/meeting
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate local-meeting-input-provider
```

