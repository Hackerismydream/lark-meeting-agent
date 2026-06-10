# Lark Meeting Agent

Lark Meeting Agent is a Feishu/Lark-native meeting workflow agent for pre-meeting briefs, live transcript understanding, post-meeting minutes, approval-gated writeback, long-term meeting memory, and source-grounded cross-meeting QA.

## Current Status

This repository contains the lifecycle implementation on top of the existing post-meeting MVP.

Implemented:

- `PreBriefWorkflow`: calendar/doc/task/memory context collection and sourced pre-briefs.
- `LiveMeetingWorkflow`: incremental transcript/event ingestion, rolling state, decision/action/risk/question candidates, and source-grounded live QA.
- `PostMeetingWorkflow`: transcript normalization, structured minutes, decisions, action items, risks, open questions, write plans, and approval-gated writes.
- `MemoryWorkflow`: layered JSONL memory for meetings, segments, minutes, decisions, action items, risks, questions, entity memories, traces, and retrieval metadata.
- `LarkToolAdapter`: the only Lark boundary, with fake and `lark-cli` providers, allowlisted operations, dry-run writes, approval checks, retry, audit, and redaction.
- Evaluation: 31 compact fixture cases with action/decision precision and recall, evidence coverage, schema success, tool safety, and QA source metrics.

Not claimed:

- no custom ASR,
- no automatic meeting bot join,
- no unapproved realtime VC control,
- no mandatory PostgreSQL/vector database service,
- no production OAuth onboarding.

Real Lark read/write paths exist through `lark-cli`, but readable meeting minutes depend on the authorized account having accessible meeting notes. Current account limitations are documented in `docs/BLOCKERS.md`.

## Current Change

```text
openspec/changes/deliver-lifecycle-meeting-agent
```

## OpenSpec Workflow

```bash
openspec list
openspec show deliver-lifecycle-meeting-agent
openspec validate deliver-lifecycle-meeting-agent
```

## Local Commands

Post-meeting fake demo:

```bash
uv run python -m nanobot.meeting.cli process \
  --transcript-file tests/fixtures/meeting/transcripts/sample_project_sync.txt \
  --provider-mode fake \
  --analyzer-mode fake \
  --create-doc \
  --create-tasks \
  --dry-run
```

Pre-brief fake demo:

```bash
uv run python -m nanobot.meeting.cli prebrief \
  --query "Alpha 项目例会" \
  --meeting-type project_sync \
  --project Alpha
```

Live meeting fake demo:

```bash
state=$(uv run python -m nanobot.meeting.cli live-start --meeting-id live-demo --title "Live Demo")
run_id=$(printf '%s' "$state" | uv run python -c 'import json,sys; print(json.load(sys.stdin)["live_run_id"])')
uv run python -m nanobot.meeting.cli live-ingest \
  --live-run-id "$run_id" \
  --meeting-id live-demo \
  --text "Alice 决定先灰度上线。" \
  --speaker Alice \
  --timestamp 00:01
uv run python -m nanobot.meeting.cli live-qa \
  --live-run-id "$run_id" \
  --question "有什么结论？"
```

Evaluation:

```bash
uv run python -m nanobot.meeting.cli evaluate \
  --cases tests/fixtures/meeting/evaluation/lifecycle_cases.json \
  --output /tmp/lma-lifecycle-eval.json
```

Validation:

```bash
uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate deliver-lifecycle-meeting-agent
```

Real demo instructions are in `docs/MVP_REAL_DEMO.md`.

Local real-mode helper:

```bash
scripts/lma-real process --latest-ended --query "项目例会" --create-doc --create-tasks --dry-run
scripts/lma-real prebrief --query "项目例会" --meeting-type project_sync --project Alpha
```
