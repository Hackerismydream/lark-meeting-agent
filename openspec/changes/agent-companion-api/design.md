# Design: Phase 2: Agent Companion API

## Architecture Principle

The macOS app is a companion client. It must communicate with the Agent Service / Companion API and must not directly call Lark APIs or execute write operations.

## Key Design Points

- Expose typed API envelopes.
- Use existing repositories/workflows.
- Enforce auth.
- Approve/reject must go through backend approval policy.
- Transcript upload may process text/json/md only.

## Required Artifacts

- `nanobot/meeting/companion_models.py`
- `nanobot/meeting/companion_api.py`
- `tests/meeting/test_companion_api.py`
- `docs/COMPANION_API.md`
- OpenSpec change files

## Validation

`uv run python -m pytest tests/meeting -q`
`uv run ruff check nanobot tests`
`openspec validate agent-companion-api`
