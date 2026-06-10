# MVP Real Demo

## Prerequisites

1. Install the project in editable mode.
2. Install and authenticate `lark-cli`.
3. For the primary real demo, prepare a currently running Feishu/Lark meeting with a 9-digit meeting number.
4. For optional historical enrichment, prepare a completed meeting with readable transcript or minutes.
5. Configure an OpenAI-compatible LLM provider.

## Install

```bash
uv pip install -e '.[dev]'
```

## lark-cli Setup

```bash
npx @larksuite/cli@latest install
lark-cli config init --new
lark-cli auth login --recommend
lark-cli auth status
```

Browser authorization may be required.

## LLM Setup

This machine stores the DeepSeek API key in macOS Keychain service
`lark-meeting-agent.deepseek-api-key`. The repo does not store the key.

Preferred helper:

```bash
scripts/lma-real status
```

The helper defaults `LARK_CLI_NO_PROXY=1` so Lark credential checks do not
transit through a local proxy unless explicitly overridden.

Manual DeepSeek OpenAI-compatible defaults:

```bash
export LMA_LLM_API_KEY="..."
export LMA_LLM_BASE_URL="https://api.deepseek.com"
export LMA_LLM_MODEL="deepseek-v4-pro"
```

Do not commit secrets.

## Fake Fixture Demo

```bash
python -m nanobot.meeting.cli process \
  --transcript-file tests/fixtures/meeting/transcripts/sample_project_sync.txt \
  --provider-mode fake \
  --analyzer-mode fake \
  --create-doc \
  --create-tasks \
  --dry-run
```

Expected:

- returns `run_id`,
- returns structured minutes,
- returns decisions and action items with evidence,
- returns WritePlan,
- does not write to Lark.

## Real Live Listener Demo

This is the primary real path. Join and leave are visible to meeting participants, so the commands require explicit approval flags.

```bash
join_json=$(scripts/lma-real live-join \
  --meeting-number <9-digit-meeting-number> \
  --approve-visible-join)
live_run_id=$(printf '%s' "$join_json" | uv run python -c 'import json,sys; print(json.load(sys.stdin)["live_run_id"])')
meeting_id=$(printf '%s' "$join_json" | uv run python -c 'import json,sys; print(json.load(sys.stdin)["meeting_id"])')

scripts/lma-real live-poll \
  --meeting-id "$meeting_id" \
  --live-run-id "$live_run_id"

scripts/lma-real live-qa \
  --live-run-id "$live_run_id" \
  --question "目前有哪些结论和待办？"

scripts/lma-real live-leave \
  --meeting-id "$meeting_id" \
  --approve-visible-leave
```

Expected:

- the bot visibly joins the in-progress meeting,
- `lark-cli vc +meeting-events` returns live event data,
- transcript/chat events become sourced live state,
- live QA returns sources or insufficient evidence,
- the bot leaves after explicit approval.

## Optional Historical Dry-run Process Demo

Preferred local helper:

```bash
scripts/lma-real process \
  --latest-ended \
  --query "项目例会" \
  --create-doc \
  --create-tasks \
  --dry-run
```

Manual equivalent:

```bash
python -m nanobot.meeting.cli process \
  --latest-ended \
  --query "项目例会" \
  --provider-mode cli \
  --analyzer-mode llm \
  --create-doc \
  --create-tasks \
  --dry-run
```

Expected if the account can read historical minutes/notes:

- calls `lark-cli` to find/fetch historical meeting notes,
- calls configured LLM,
- returns structured minutes,
- returns WritePlan,
- does not write to Lark.

## Approval Demo

Approve only reviewed operation IDs:

```bash
python -m nanobot.meeting.cli approve \
  --provider-mode cli \
  --run-id <run_id> \
  --operation-ids <operation_id_1,operation_id_2>
```

Expected:

- executes only selected operations,
- returns Lark doc/task/message results,
- records audit events,
- leaves unapproved operations skipped.

First demo should approve docs/tasks only. Keep `im.send` dry-run until the target `chat_id` is safe.

## QA Demo

```bash
python -m nanobot.meeting.cli qa \
  --question "这次会议决定了什么？有哪些待办？"
```

Expected:

- answer is based on local `.lark_meeting_agent/` knowledge,
- sources cite meeting and segment IDs,
- insufficient evidence is reported when no supporting source exists.

## Feishu/nanobot Chat Flow

After enabling the Feishu channel, expected flow:

User:

```text
整理最近一场项目例会，先不要写入飞书
```

Agent should call:

```text
lark_meeting(action="process", provider_mode="cli", analyzer_mode="llm", dry_run=true)
```

User:

```text
确认创建文档和任务
```

Agent should call:

```text
lark_meeting(action="approve", run_id="...", operation_ids=[...])
```

Feishu channel is not required for automated tests.
