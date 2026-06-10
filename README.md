# Lark Meeting Agent

Lark Meeting Agent is a Feishu/Lark-native meeting workflow agent. The MVP is post-meeting only and is specified through OpenSpec before application code is implemented.

## Current Status

This repository contains the nanobot-based MVP implementation.

Architecture pivot: the runtime is HKUDS/nanobot v0.2.1. Lark Meeting Agent is implemented as a nanobot source-based meeting-domain extension, not as a standalone FastAPI application.

## Current Change

```text
openspec/changes/bootstrap-lark-meeting-agent
```

## OpenSpec Workflow

```bash
openspec list
openspec show bootstrap-lark-meeting-agent
openspec validate bootstrap-lark-meeting-agent
```

## MVP Commands

Fake local demo:

```bash
python -m nanobot.meeting.cli process \
  --transcript-file tests/fixtures/meeting/transcripts/sample_project_sync.txt \
  --provider-mode fake \
  --analyzer-mode fake \
  --create-doc \
  --create-tasks \
  --dry-run
```

Validation:

```bash
python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py
python -m pytest tests/meeting -q
ruff check nanobot tests
openspec validate bootstrap-lark-meeting-agent
```

Real demo instructions are in `docs/MVP_REAL_DEMO.md`.

Local real-mode helper:

```bash
scripts/lma-real process --latest-ended --query "项目例会" --create-doc --create-tasks --dry-run
```
