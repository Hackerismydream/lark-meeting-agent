# Proposal: Phase 6: Cross-meeting Search and Local Transcript Upload

## Why

V1.1 moves macOS into a dedicated release after V1.0 production bot readiness.

This change supports the macOS companion app while preserving the backend Agent as the source of truth.

## What

Add cross-meeting search UI and local transcript upload flow for text-based files.

## Scope

- Search query sends to backend.
- Answers display sources.
- Insufficient evidence state is visible.
- Transcript upload accepts txt/md/json.
- Upload creates run or returns typed error.

## Non-goals

- No ASR.
- No audio transcription.
- No local LLM processing.
