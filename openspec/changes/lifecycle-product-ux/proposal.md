# Proposal: Lifecycle Product UX

## Intent

Implement V1.0 phase `lifecycle-product-ux` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Define canonical commands and Chinese aliases.
- Process/prebrief/live/status/qa approval flow has predictable responses.
- Approval prompt is safe and explicit.
- Status without run_id can show recent pending runs for authorized user/chat.
- No vague '确认' auto-approves without explicit run/operation context.

## Scope

This change covers:

- Define canonical commands and Chinese aliases.
- Process/prebrief/live/status/qa approval flow has predictable responses.
- Approval prompt is safe and explicit.
- Status without run_id can show recent pending runs for authorized user/chat.
- No vague '确认' auto-approves without explicit run/operation context.
- User messages distinguish dry-run, approved, rejected, failed, insufficient evidence.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- Snapshot tests cover approval prompt, status, prebrief, live QA, insufficient evidence.
- Chinese aliases tested.
- Unsafe ambiguous approval returns clarification, not write.
