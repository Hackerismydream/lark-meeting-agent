# macOS Search and Transcript Upload

Phase 6 adds cross-meeting search and local text transcript upload to the macOS companion app.

The macOS app still delegates all meeting intelligence and write planning to the backend Companion API.

## Search

The search view calls:

```text
POST /v1/search
```

The response displays:

- answer text,
- insufficient evidence state,
- source citations with `meeting_id` and `segment_id`,
- speaker and timestamp when present.

Answers without evidence are displayed as insufficient evidence rather than being treated as confirmed facts.

## Upload

The upload view calls:

```text
POST /v1/upload/transcript
```

Supported local file extensions:

```text
.txt
.md
.json
```

Unsupported files are rejected before upload. V1.1 does not implement ASR, audio transcription, local LLM processing, or local meeting analysis inside the macOS app.

Upload options only request backend dry-run write planning:

- create doc preview,
- create task previews,
- prepare IM preview.

Real writes still require backend approval and LarkToolAdapter execution.

## Validation

Validated on this workstation:

```bash
swift build --package-path apps/macos/LarkMeetingAgent
swift run --package-path apps/macos/LarkMeetingAgent LarkMeetingAgentCoreSmokeTests
uv run python -m pytest tests/meeting -q
openspec validate macos-search-upload
```

`swift test --package-path apps/macos/LarkMeetingAgent` remains replaced by the executable smoke runner in this Command Line Tools environment.
