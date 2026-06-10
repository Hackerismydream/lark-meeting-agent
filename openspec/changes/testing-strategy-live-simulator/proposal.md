# Proposal: Testing Strategy and Live Meeting Simulator

## Intent

Implement V1.0 phase `testing-strategy-live-simulator` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Adopt text/event-first as primary development and evaluation path.
- Build a LiveMeetingSimulator that emits Lark-like event pages with has_more/page_token.
- Support transcript, chat, participant, share, malformed, duplicate, out-of-order, and prompt-injection events.
- Create 8 scenario fixtures covering customer, project weekly, requirement review, tech review, incident, 1:1, sales/CS, long retrospective.
- Implement live and lifecycle replay with metrics JSON and failures JSON.

## Scope

This change covers:

- Adopt text/event-first as primary development and evaluation path.
- Build a LiveMeetingSimulator that emits Lark-like event pages with has_more/page_token.
- Support transcript, chat, participant, share, malformed, duplicate, out-of-order, and prompt-injection events.
- Create 8 scenario fixtures covering customer, project weekly, requirement review, tech review, incident, 1:1, sales/CS, long retrospective.
- Implement live and lifecycle replay with metrics JSON and failures JSON.
- Add Hypothesis for event conversion fuzzing and Freezegun for time tests.
- Keep real Lark and real LLM tests opt-in only.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- 8 scenarios load and replay.
- Transcript and chat events can become source-grounded live QA sources.
- page_token/has_more/duplicate event_id/malformed event are covered.
- Metrics JSON and failures JSON are generated.
- Safety matrix covers unknown tool, unapproved write, prompt injection, approval bypass.
- No test requires real Lark credentials or real LLM keys.
