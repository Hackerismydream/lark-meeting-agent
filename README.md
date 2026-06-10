# Lark Meeting Agent

Lark Meeting Agent is a Feishu/Lark-native meeting workflow agent. The MVP is post-meeting only and is specified through OpenSpec before application code is implemented.

## Current Status

This repository is in the OpenSpec bootstrap phase.

Architecture pivot: the target runtime is HKUDS/nanobot v0.2.1. Lark Meeting Agent should be implemented later as a nanobot fork or source-based meeting-domain extension, not as a standalone FastAPI application.

No application code exists yet. Do not create `app/`, `nanobot/`, `tests/`, `pyproject.toml`, `Dockerfile`, migrations, real Lark integration, real LLM integration, frontend code, or runtime files in this phase.

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

Do not implement application code until the bootstrap OpenSpec artifacts and nanobot pivot have been reviewed and accepted.
