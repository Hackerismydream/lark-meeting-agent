# V1.2 Roadmap

V1.2 should turn the V1.1 companion shell into a stronger product demo without weakening backend approval and LarkToolAdapter boundaries.

## Highest Priority

1. Mount Companion API behind a real local/remote HTTP server with bearer auth, request logging redaction, and CORS policy.
2. Add real app bundle packaging with Xcode project, app icon, entitlements, hardened runtime, signing, notarization, and Gatekeeper verification.
3. Add fixture-backed demo dataset covering approvals, pre-briefs, traces, search, insufficient evidence, and uploads.
4. Replace executable smoke runner with full Swift test target once full Xcode test runtime is available.

## Product Enhancements

1. Better menu bar navigation with separate windows for approvals, pre-brief, trace, search, and upload.
2. Operation diff/preview rendering for docs, tasks, and IM messages.
3. Trace filtering by stage, error, tool call, write result, and timestamp.
4. Search filters for project, customer, person, time range, and meeting type.
5. Safer upload progress, retry, and typed backend error display.

## Later Work

1. Live meeting control UI for explicit join/leave only after backend live-listener gates are stable.
2. Desktop notifications with smarter de-duplication.
3. Signed and notarized beta release.
4. Admin policy UI for allowed users and approval scopes.

## Still Out Of Scope Unless Re-approved

- macOS as a standalone Agent runtime.
- Direct Lark API calls from Swift.
- Local ASR/audio transcription.
- Unapproved writes.
- App Store release claims before actual review and approval.
