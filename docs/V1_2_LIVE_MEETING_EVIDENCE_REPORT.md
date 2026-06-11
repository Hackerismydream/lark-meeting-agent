# V1.2 Live Meeting Evidence Report

## Version Definition

V1.2 adds a reproducible live meeting evidence runner. The version is not a voice assistant and does not implement custom ASR. It turns the live meeting product path into a testable engineering gate:

```text
explicit visible join approval
-> dry-run join preview
-> real join attempt
-> event poll when join succeeds
-> live QA when events exist
-> explicit visible leave
-> sanitized evidence pack
```

## Files Added

- `nanobot/meeting/live_evidence.py`
- `scripts/live/run_live_meeting_evidence.py`
- `tests/meeting/test_live_evidence_runner.py`
- `docs/LIVE_MEETING_TALK_AGENT_REFERENCE_REVIEW.md`
- `docs/V1_2_LIVE_MEETING_EVIDENCE_REPORT.md`
- `openspec/changes/v1-2-live-meeting-evidence/`

## Commands

Dry run:

```bash
uv run python scripts/live/run_live_meeting_evidence.py \
  --workspace /Users/martinlos/lark-meeting-agent \
  --meeting-number 909401086 \
  --provider-mode cli
```

Approved real attempt:

```bash
LARK_CLI_NO_PROXY=1 uv run python scripts/live/run_live_meeting_evidence.py \
  --workspace /Users/martinlos/lark-meeting-agent \
  --meeting-number "909 401 086" \
  --provider-mode cli \
  --out-root runs/live_real \
  --approve-visible-join \
  --approve-visible-leave
```

Equivalent project CLI:

```bash
uv run python -m nanobot.meeting.cli \
  --workspace /Users/martinlos/lark-meeting-agent \
  live-evidence \
  --meeting-number 909401086 \
  --provider-mode cli \
  --approve-visible-join \
  --approve-visible-leave
```

## Real Meeting Result

Meeting number: `909401086`.

Evidence pack path:

```text
runs/live_real/909401086/
```

This path is intentionally ignored by git.

Observed status on 2026-06-11:

- status: `blocked`
- failure_class: `permission`
- event_count: `0`
- raw_event_shapes: not generated because join failed before polling
- dry-run endpoint: `/open-apis/vc/v1/bots/join`
- dry-run body shape: `join_identify.meeting_no = 909401086`, `join_type = 1`
- real API error: `121003 / HTTP 403: no permission`

The local user auth was already valid and included the expected meeting bot scopes in earlier verification. This means the current blocker is not ordinary missing local login. The likely gate is tenant-side app permission, product gray rollout, or app availability for meeting bot join.

## What This Proves

- The project has a real-data-driven live meeting gate, not only fixture tests.
- Visible join/leave cannot be executed silently; approval flags are required.
- The failure is captured as a structured blocker with an audit trail.
- Feishu API calls still stay inside `LarkToolAdapter`.
- Private live meeting data is not committed.

## Next Engineering Step

After Feishu tenant/app access to `/vc/v1/bots/join` is enabled, rerun the approved real attempt. The next V1.2 subtask is then to inspect sanitized `raw_event_shapes.json`, update event conversion for any real event fields, and rerun live QA against actual meeting transcript/chat evidence.

