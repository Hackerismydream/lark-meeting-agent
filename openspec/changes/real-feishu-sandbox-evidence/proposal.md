# Proposal: Real Feishu Sandbox Evidence

## Summary

Add sandbox demo scripts and evidence reports that validate the product chain against the user's real Feishu environment while keeping public meeting fixtures as the meeting content source.

## Scope

- Real calendar read through `LarkToolAdapter`.
- Public fixture transcript through PostMeetingWorkflow.
- Dry-run WritePlan by default.
- Optional sandbox-only writes gated by `LMA_DEMO_ENABLE_REAL_WRITES=1` and explicit `--approve`.
- Source-grounded QA evidence from local fixture memory.
- Redacted evidence packs and screenshot checklist.

## Non-goals

- No live meeting join.
- No private meeting transcript ingestion.
- No automatic screenshots.
- No unapproved writeback.
- No production metric claims.
