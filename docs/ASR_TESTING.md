# ASR Testing

Audio and ASR are not the V1.0 MVP path.

The primary development and evaluation path is text/event-first:

```text
simulated Lark event pages
-> event conversion
-> live state
-> source-grounded QA
-> post-meeting dry-run WritePlan
```

Audio can be added later as an optional robustness track. ASR error metrics and Agent extraction metrics must be measured separately.

Possible future stack:

- faster-whisper for ASR,
- pyannote.audio for speaker diarization,
- Silero VAD for voice activity detection.

Do not claim ASR support until it is implemented and evaluated.
