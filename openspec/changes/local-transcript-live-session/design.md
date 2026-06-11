# Design: Local Transcript Live Session

## Version Step

This is the first V2.0 step toward Local Meeting Capture for Mac. The input source is an append-only transcript file, not hidden audio capture.

```text
append-only transcript file
-> LocalTranscriptProvider append poll
-> LiveMeetingEvent transcript deltas
-> LiveMeetingWorkflow ingest
-> live QA
-> optional post-meeting minutes / WritePlan dry-run
```

## Provider Hardening

Input providers expose explicit capabilities and typed errors. Append mode keeps a session `RUNNING` after each poll, advances a cursor by canonical segment count, and never re-emits already seen segments.

## Runner

`LocalTranscriptLiveRunner` owns the local session lifecycle:

- start provider session and live workflow state,
- poll new transcript segments,
- feed events into `LiveMeetingWorkflow`,
- answer live QA from current live state,
- stop the session,
- optionally finalize accumulated transcript into post-meeting minutes and a dry-run write plan.

## Writeback Boundary

Local input providers do not write to Feishu. Finalization uses existing post-meeting workflow with `provider_mode=fake` and dry-run write plans. Real writeback still requires the existing approval path and `LarkToolAdapter`.

## Privacy

This step only reads an explicit local transcript path selected by the user. It does not implement ScreenCaptureKit, microphone capture, ASR, diarization, or hidden monitoring.

