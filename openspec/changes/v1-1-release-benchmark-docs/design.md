# Design: Phase 8: V1.1 Release Benchmark and Docs

## Architecture Principle

The macOS app is a companion client. It must communicate with the Agent Service / Companion API and must not directly call Lark APIs or execute write operations.

## Key Design Points

- Delivery report.
- Demo runbook.
- Screenshots checklist.
- Known limitations.
- Resume-safe wording.
- V1.2 roadmap.

## Required Artifacts

- `docs/V1_1_DELIVERY_REPORT.md`
- `docs/V1_1_DEMO_RUNBOOK.md`
- `docs/V1_1_SCREENSHOTS_CHECKLIST.md`
- `docs/V1_2_ROADMAP.md`
- OpenSpec change files

## Validation

`openspec validate v1-1-release-benchmark-docs`
