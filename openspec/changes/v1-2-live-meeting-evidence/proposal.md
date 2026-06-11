# Proposal: V1.2 Live Meeting Evidence

## Summary

Add a real-meeting evidence runner for the live meeting path. The runner uses a user-provided 9-digit meeting number, produces a sanitized evidence pack, classifies blockers, and records enough data to continue development without losing the exact real-world failure.

## Motivation

The current live smoke command returns a compact JSON result. That is not enough for real-data-driven development because the key failure details, dry-run request shape, auth state, raw event shapes, and blocker guidance are scattered across terminal output.

The reference project `hataketed7977/lark-meeting-talk-agent` shows that a live meeting product needs a durable runtime/evidence loop around join, realtime events, current meeting memory, and shutdown. V1.2 adopts the evidence and lifecycle parts without importing its ASR/TTS/realtime audio runtime.

## Scope

- New live evidence runner and CLI command.
- Sanitized evidence pack under `runs/live_real/<meeting_number>/`.
- Join dry-run preview.
- Real join / poll / QA / leave when approved.
- Blocker classification for permission, gray release, meeting not found, meeting ended, no events, and unknown failures.
- Documentation for the `909401086` real meeting blocker.

## Non-goals

- No custom ASR.
- No TTS.
- No Feishu realtime audio WebSocket integration.
- No wake-word dialog runtime.
- No unapproved visible join or leave.
- No private transcript persistence.

## Validation

```bash
uv run python -m compileall nanobot/meeting scripts/live
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests scripts
openspec validate v1-2-live-meeting-evidence
```
