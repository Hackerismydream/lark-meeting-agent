# V1.1 Demo Runbook

This demo shows the macOS companion app controlling the backend Agent Service.

## Prerequisites

- Backend Companion API is running.
- API base URL is configured in macOS settings.
- Bearer token is stored in Keychain if backend auth is enabled.
- Fixture data exists for pending WritePlans, runs, traces, and meeting memory.

## Demo Flow

1. Launch the menu bar app.
2. Refresh Agent status and show provider/analyzer/storage status.
3. Open approval inbox.
4. Show pending operations with operation IDs, previews, targets, approval status, and execution status.
5. Select a single operation and approve selected.
6. Show the backend result after refresh.
7. Generate a pre-brief from a query or meeting ID.
8. Show sections, warnings, and source citations.
9. Inspect a run and trace timeline.
10. Show write results and trace event data.
11. Search meeting memory.
12. Show answer sources with meeting ID and segment ID.
13. Show insufficient evidence state with a query that lacks sources.
14. Upload a `.md` or `.txt` transcript.
15. Show created backend run and approval-required write plan.
16. Attempt to upload an audio file and show local rejection.

## What To Say

```text
The macOS app is a companion surface. It does not call Feishu/Lark APIs directly. Every write still goes to the backend approval path and LarkToolAdapter.
```

## What Not To Claim

- Do not claim ASR.
- Do not claim realtime audio capture.
- Do not claim signing or notarization.
- Do not claim App Store distribution.
- Do not claim the macOS app can operate without the backend Agent Service.
