# Proposal: Phase 1: macOS Product Contract and Agent API Contract

## Why

V1.1 moves macOS into a dedicated release after V1.0 production bot readiness.

This change supports the macOS companion app while preserving the backend Agent as the source of truth.

## What

Define V1.1 macOS companion app product boundaries, backend API contract, data models, security rules, and UX flows before implementation.

## Scope

- macOS app is a companion client, not primary runtime.
- App never writes to Lark directly.
- Backend API is a thin adapter over existing workflows.
- Keychain is required for persisted tokens.
- Approval UX must display run_id and operation IDs.

## Non-goals

- No Swift app yet.
- No backend implementation yet.
- No ASR.
- No direct Lark writes.
