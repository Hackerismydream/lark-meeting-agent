# Proposal: Meeting Data Bootstrap and Feishu Chain Tiny30

## Why

The project does not yet have real customer meeting data. V1 needs reproducible, real-human meeting content for development while preserving a separate real Feishu product-chain demo for calendar, docs, tasks, and IM workflow evidence.

## What Changes

- Add canonical `MeetingFixture` schemas for public meeting datasets.
- Add deterministic tiny10 preparation paths for MeetingBank, QMSum, and VCSum.
- Add fixture storage, deterministic sampling, transcript streaming, Feishu-like context wrapping, and local mock Lark tools.
- Add a tiny30 evaluation runner and report artifacts.
- Add dry-run-first Feishu demo scripts that use the existing Lark boundary and require explicit opt-in for real sandbox writes.
- Document dataset cards, download commands, governance, evaluation tasks, and delivery status.

## Scope

Included:

- MeetingBank, QMSum, and VCSum only.
- Toy raw samples for tests.
- Local artifacts under `runs/meeting_eval/<run_id>/`.
- OpenSpec, docs, scripts, and tests.

Excluded:

- AMI/ICSI datasets.
- Audio processing or ASR.
- CI calls to real Feishu APIs.
- Raw public datasets committed to git.
- Claims that public dataset metrics are production Feishu metrics.

## Impact

This creates the reproducible data bridge:

```text
public real-human meeting data
-> canonical MeetingFixture
-> FeishuLikeMeetingContext
-> current meeting workflows / mock Lark tools
-> local eval artifacts and reports
```

Real Feishu demo scripts remain opt-in and sandbox-only.
