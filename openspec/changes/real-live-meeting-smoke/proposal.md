# Proposal: Real Live Meeting Smoke Gate

## Intent

Implement V1.0 phase `real-live-meeting-smoke` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Add `scripts/lma-real live-smoke` or equivalent command.
- No real Lark smoke in CI by default.
- Require explicit --meeting-number and visible join/leave approval flags.
- Classify failures: permission, gray, not in meeting, meeting ended, no events, unknown event shape, page token issue.
- Record sanitized raw event shape samples when user explicitly requests export.

## Scope

This change covers:

- Add `scripts/lma-real live-smoke` or equivalent command.
- No real Lark smoke in CI by default.
- Require explicit --meeting-number and visible join/leave approval flags.
- Classify failures: permission, gray, not in meeting, meeting ended, no events, unknown event shape, page token issue.
- Record sanitized raw event shape samples when user explicitly requests export.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- No meeting number gives clear error.
- Dry-run smoke path does not join.
- Real smoke command exists and documents prerequisites.
- LIVE_LARK_SMOKE_RESULTS.md records not-run / run / blocked status honestly.
