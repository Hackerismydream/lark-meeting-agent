# Proposal: Materialize Tiny30 Real Datasets

## Why

The meeting agent needs reproducible real-human meeting data for development and evaluation before real customer meeting data exists. The repository already has meeting-data scaffolding; this change hardens it into a deterministic tiny30 materialization flow.

## What Changes

- Harden MeetingBank, QMSum, and VCSum adapters against real raw dataset layouts.
- Add deterministic `--limit` and `--seed` support to preparation scripts.
- Generate manifest rows and a fixture lock for produced tiny30 fixtures.
- Add governance around raw data and processed fixture commits.
- Add `docs/TINY30_DATA_REPORT.md`.

## Non-Goals

- No Feishu API calls.
- No real LLM calls.
- No UI screenshots or Computer Use.
- No audio or ASR.
- No AMI / ICSI.
- No full-dataset benchmark claim.

## Output

The intended local output is:

```text
data/processed/meeting_fixtures/meetingbank/tiny10/*.json
data/processed/meeting_fixtures/qmsum/tiny10/*.json
data/processed/meeting_fixtures/vcsum/tiny10/*.json
data/manifests/*_tiny10_manifest.jsonl
data/manifests/fixture_lock.json
docs/TINY30_DATA_REPORT.md
```

Raw data remains local under `data/raw/` and is never committed.
