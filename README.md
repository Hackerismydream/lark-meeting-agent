# Lark Meeting Agent

Lark Meeting Agent is a Feishu/Lark-native lifecycle local MVP for pre-meeting briefs, live meeting listening, post-meeting minutes, approval-gated writeback, long-term meeting memory, and source-grounded cross-meeting QA.

## Current Status

This repository contains a lifecycle local MVP. The product's primary real transcript path is now live meeting listening: a visible bot joins an in-progress meeting, polls Lark meeting events, converts transcript/chat deltas into live state, and answers sourced in-meeting questions. Historical Feishu minutes/notes are optional enrichment, not the main gate.

Implemented:

- `PreBriefWorkflow`: read-only calendar/doc/task/memory context collection and sourced pre-briefs using retrieval plus templates.
- `LiveMeetingWorkflow` and `LiveLarkMeetingWorkflow`: incremental supplied transcript/event ingestion plus controlled real Lark live join, event polling, rolling state, decision/action/risk/question candidates, and source-grounded live QA.
- `PostMeetingWorkflow`: transcript normalization, structured minutes, decisions, action items, risks, open questions, write plans, and approval-gated writes.
- `MemoryWorkflow`: layered JSONL memory for meetings, segments, minutes, decisions, action items, risks, questions, entity memories, traces, and retrieval metadata.
- `LarkToolAdapter`: the only Lark boundary, with fake and `lark-cli` providers, allowlisted operations, dry-run writes, approval checks, retry, audit, and redaction.
- Evaluation: 31 compact deterministic fixture regression cases with action/decision precision and recall, evidence coverage, schema success, tool safety, and QA source metrics.

Not claimed:

- no custom ASR,
- no invisible or automatic meeting capture,
- no unapproved realtime VC control,
- no mandatory PostgreSQL/vector database service,
- no production OAuth onboarding.

Real Lark paths exist through `lark-cli`. The live listener path requires a currently running 9-digit meeting number and explicit approval because join/leave are visible to participants. Readable historical minutes still depend on account access, but that is no longer the primary product blocker. Current account limitations are documented in `docs/BLOCKERS.md`; operation-level verification status is tracked in `docs/LARK_CLI_VERIFICATION_MATRIX.md`.

## Current Change

```text
openspec/changes/deliver-lifecycle-meeting-agent
openspec/changes/harden-lifecycle-agent-evidence-and-real-gates
openspec/changes/production-feishu-bot
openspec/changes/macos-companion-app
openspec/changes/pivot-live-meeting-listener
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
state=$(uv run python -m nanobot.meeting.cli live-join \
  --meeting-number 123456789 \
  --provider-mode fake \
  --approve-visible-join)
run_id=$(printf '%s' "$state" | uv run python -c 'import json,sys; print(json.load(sys.stdin)["live_run_id"])')
meeting_id=$(printf '%s' "$state" | uv run python -c 'import json,sys; print(json.load(sys.stdin)["meeting_id"])')
uv run python -m nanobot.meeting.cli live-poll \
  --meeting-id "$meeting_id" \
  --live-run-id "$run_id" \
  --provider-mode fake
uv run python -m nanobot.meeting.cli live-qa \
  --live-run-id "$run_id" \
  --question "有什么结论和待办？"
```

Manual supplied-event demo:

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

Production planning docs:

- `docs/PRODUCTION_FEISHU_BOT_DEPLOYMENT.md`
- `docs/PRODUCTION_SECURITY_CHECKLIST.md`
- `docs/PRODUCTION_RUNBOOK.md`
- `docs/REAL_TRANSCRIPT_GATE.md`
- `docs/LIVE_MEETING_LISTENER.md`
- `docs/OAPI_PROVIDER_PLAN.md`
- `docs/MACOS_APP_ROADMAP.md`

Local real-mode helper:

```bash
scripts/lma-real process --latest-ended --query "项目例会" --create-doc --create-tasks --dry-run
scripts/lma-real prebrief --query "项目例会" --meeting-type project_sync --project Alpha
scripts/lma-real live-join --meeting-number <9-digit-meeting-number> --approve-visible-join
scripts/lma-real live-poll --meeting-id <returned-long-meeting-id> --live-run-id <returned-live-run-id>
scripts/lma-real live-leave --meeting-id <returned-long-meeting-id> --approve-visible-leave
```
