# Proposal: Phase 7: macOS Security, Packaging, and Release

## Why

V1.1 moves macOS into a dedicated release after V1.0 production bot readiness.

This change supports the macOS companion app while preserving the backend Agent as the source of truth.

## What

Harden macOS app security and prepare local release packaging/manual QA.

## Scope

- Keychain token storage.
- No token logs.
- Production environment warning.
- Manual QA checklist.
- Packaging docs.
- Signing/notarization docs but do not claim completed unless actually done.

## Non-goals

- Do not claim App Store release.
- Do not claim notarization unless done.
- No direct Lark writes.
