# Design: Local Meeting Input Provider

## Provider Boundary

The new input layer is intentionally narrow:

```text
MeetingInputProvider.start(config)
MeetingInputProvider.poll(session)
MeetingInputProvider.stop(session)
```

Every provider emits canonical `LiveMeetingEvent` objects and, when transcript text exists, canonical `TranscriptSegment` objects. Downstream live QA, post-meeting analysis, memory, and writeback continue to consume existing meeting-domain models.

## Providers

### LocalTranscriptProvider

Reads a user-provided transcript file and replays it as `transcript_delta` events. Supported file content uses the existing `TranscriptNormalizer` text / JSON behavior.

### LocalAudioFileProvider

Registers a user-provided local audio file. This change does not implement ASR. If a transcript sidecar is provided, the sidecar is normalized and replayed as `transcript_delta` events. If no sidecar is provided, the provider emits one marker event recording that an audio file was supplied and no transcript is available yet.

## Feishu Compatibility

`FeishuOfficialLiveProvider` remains the official live path. This change does not remove or weaken `LiveLarkMeetingWorkflow`; it creates a provider-agnostic layer that can later wrap that workflow while local providers unblock development.

## Privacy

Local providers are user-initiated and file-based in this change. They do not perform hidden monitoring, do not capture microphone or system audio, and do not write to Feishu. Feishu writes remain approval-gated through existing `WritePlan` and `LarkToolAdapter`.

## Future Work

Later changes may add ScreenCaptureKit live system-audio capture, microphone live streaming, ASR integration, and diarization behind the same provider boundary.

