# Proposal: V1 Release, Benchmark, and Docs

## Intent

Implement V1.0 phase `v1-release-benchmark-docs` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Summarize implemented capabilities without exaggeration.
- Separate fixture metrics, optional LLM metrics, real Lark smoke, blocked/unverified capabilities.
- Provide demo flows: fake lifecycle replay, real live smoke, production bot dry-run, approval demo.
- List V1 known limitations.
- Define V1.1 roadmap: macOS companion app, audio/ASR, richer RAG, production deployment hardening.

## Scope

This change covers:

- Summarize implemented capabilities without exaggeration.
- Separate fixture metrics, optional LLM metrics, real Lark smoke, blocked/unverified capabilities.
- Provide demo flows: fake lifecycle replay, real live smoke, production bot dry-run, approval demo.
- List V1 known limitations.
- Define V1.1 roadmap: macOS companion app, audio/ASR, richer RAG, production deployment hardening.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- Docs are internally consistent.
- No claim of production deployment unless smoke exists.
- No claim of ASR/macOS if not implemented.
- Benchmark report includes commit, fixture version, model profile, test command results.
