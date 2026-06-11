# macOS Manual QA

Use this checklist before describing V1.1 as ready for a demo.

## Setup

- [ ] Start backend Agent Service with Companion API mounted.
- [ ] Configure local API base URL in Settings.
- [ ] Store bearer token in Keychain if backend requires auth.
- [ ] Confirm environment label is accurate.
- [ ] Confirm production warning appears for production-like labels.

## Status

- [ ] Menu bar app launches.
- [ ] Agent status refresh succeeds against local backend.
- [ ] Bad token or wrong URL shows a safe failure message.
- [ ] Token is not printed in terminal output or UI.

## Approvals

- [ ] Pending WritePlans appear.
- [ ] Each operation shows operation ID, type, preview, target, approval status, and execution status.
- [ ] Approve button is disabled until at least one operation is selected.
- [ ] Approving selected operations sends explicit operation IDs to backend.
- [ ] Reject run calls backend reject endpoint.
- [ ] No direct Lark writes occur from macOS.

## Pre-Brief and Trace

- [ ] Today's meetings view reflects backend source status.
- [ ] Pre-brief generation displays sections, warnings, and sources.
- [ ] Run list loads recent runs.
- [ ] Run trace displays stages, messages, event data, errors, and write results.
- [ ] Trace inspection cannot trigger approval or writes.

## Search and Upload

- [ ] Search displays answer and source citations.
- [ ] Insufficient evidence is visible.
- [ ] Source citations include meeting ID and segment ID when backend provides them.
- [ ] `.txt`, `.md`, and `.json` transcript uploads work.
- [ ] `.mp3`, `.wav`, `.m4a`, and other audio files are rejected.
- [ ] Upload creates a backend run or returns a typed backend error.
- [ ] Upload does not claim ASR/audio transcription.

## Packaging

- [ ] Swift package build passes.
- [ ] Smoke runner passes.
- [ ] xcodebuild status is documented honestly.
- [ ] Signing status is documented honestly.
- [ ] Notarization status is documented honestly.
