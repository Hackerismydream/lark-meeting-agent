# Proposal: Harden Live Listener Before Real Smoke

## Intent

Implement V1.0 phase `harden-live-listener-real-smoke` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Validate meeting_number as exactly 9 digits before real join.
- Redact password/passcode/meeting_password from logs and audit.
- Map chat_received/message_received to live state sources, not marker-only events.
- Track participant and share events in live timeline.
- Persist and reuse page_token / next_page_token.

## Scope

This change covers:

- Validate meeting_number as exactly 9 digits before real join.
- Redact password/passcode/meeting_password from logs and audit.
- Map chat_received/message_received to live state sources, not marker-only events.
- Track participant and share events in live timeline.
- Persist and reuse page_token / next_page_token.
- Deduplicate event_id across repeated polls.
- Handle has_more explicitly.
- Ensure live join/leave cannot bypass production access policy.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- Invalid meeting_number is rejected.
- Password/passcode redaction is tested.
- chat event becomes QA source.
- duplicate event_id does not duplicate state.
- page_token persists and is reused.
- join/leave without approval is rejected.
- OpenSpec validates.
