# Demo Runbook

## Fake Post-Meeting Flow

```text
/meeting process Alpha
/meeting status
/meeting approve <run_id> <operation_id>
```

Expected:

1. Process returns `approval_required`.
2. Status lists the pending run.
3. Approve executes only selected operation IDs.

## Pre-brief

```text
帮我准备 Alpha 项目例会
```

Expected: a structured pre-brief JSON response with sections and source references.

## Live QA

For a local supplied-event demo:

```bash
uv run python -m nanobot.meeting.cli live-start --meeting-id live-demo --title "Live Demo"
uv run python -m nanobot.meeting.cli live-ingest --live-run-id <live_run_id> --meeting-id live-demo --text "Alice 决定先灰度上线。" --speaker Alice --timestamp 00:01
```

Then ask:

```text
/meeting live-qa <live_run_id> 有什么结论？
```

Expected: source-grounded answer with meeting and segment references.

## Ambiguous Approval Safety

```text
确认
```

Expected: `clarification_required`, not a write.
