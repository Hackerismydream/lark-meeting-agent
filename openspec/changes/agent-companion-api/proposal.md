# Proposal: Phase 2: Agent Companion API

## Why

V1.1 moves macOS into a dedicated release after V1.0 production bot readiness.

This change supports the macOS companion app while preserving the backend Agent as the source of truth.

## What

Implement a thin backend companion API over existing meeting workflows and repositories so macOS can safely observe and control the Agent.

## Scope

- Expose typed API envelopes.
- Use existing repositories/workflows.
- Enforce auth.
- Approve/reject must go through backend approval policy.
- Transcript upload may process text/json/md only.

## Non-goals

- No macOS UI yet.
- No direct Lark writes beyond existing backend approval path.
- No new Agent runtime.
