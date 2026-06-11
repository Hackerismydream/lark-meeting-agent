# lark-meeting-talk-agent Reference Review

Reviewed reference: `hataketed7977/lark-meeting-talk-agent`.

## What Helps This Project

The reference project confirms that the product direction should not depend on historical Feishu Minutes. Its useful pattern is a live meeting loop:

```text
explicit meeting join
-> current meeting event/audio stream
-> in-memory meeting context
-> stateful response loop
-> cleanup on leave
```

The parts that map well to Lark Meeting Agent are:

- current-meeting scoped state instead of treating every request as an isolated summarization task,
- lifecycle states such as waiting, engaged, speaking, and leaving,
- continuous event ingestion with a bounded meeting memory,
- cleanup and artifact finalization after leaving,
- a single-process developer path for smoke testing before larger deployment work.

## What We Should Not Copy In V1.2

The reference project is a voice meeting assistant. Lark Meeting Agent V1.2 is not adopting its ASR, TTS, realtime audio WebSocket, or wake-word pipeline.

Those pieces are intentionally deferred because the current product gate is earlier: Feishu must allow a bot to visibly join a live meeting and read meeting events. Until `/vc/v1/bots/join` works in the target tenant, ASR/TTS work would add complexity without validating the Feishu product chain.

## V1.2 Adaptation

V1.2 implements the reference lesson as a live evidence loop:

```text
dry-run join preview
-> approved visible join
-> event poll
-> live state update
-> source-grounded live QA
-> approved visible leave
-> evidence pack or blocker report
```

All Feishu operations still go through `LarkToolAdapter`. Join and leave remain approved visible write operations. The runner writes sanitized local evidence under `runs/live_real/<meeting_number>/` and keeps raw private meeting content out of git.

