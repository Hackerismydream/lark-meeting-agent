# Design: Deliver Nanobot Meeting MVP

## Summary

The implementation adds a deterministic post-meeting workflow as a meeting-domain extension inside nanobot v0.2.1. nanobot remains the runtime base; the meeting code owns only the domain lifecycle, schemas, safe Lark adapter, memory persistence, and entrypoint wrapper.

## Runtime Shape

```text
nanobot channel / WebUI / CLI / tool call
  -> lark_meeting tool
  -> PostMeetingWorkflow
      -> resolve meeting or transcript
      -> fetch transcript through LarkToolAdapter when needed
      -> normalize transcript
      -> analyze meeting
      -> build WritePlan
      -> persist structured knowledge
      -> return approval_required or completed
  -> approve selected operation IDs
      -> LarkToolAdapter
      -> approved docs.create/task.create/im.send only
      -> audit and persist results
  -> QA
      -> MeetingMemoryStore
      -> answer with meeting/segment sources
```

## Code Placement

```text
nanobot/meeting/
  schemas.py
  errors.py
  normalizer.py
  analyzer.py
  prompts.py
  renderers.py
  write_plan.py
  lark_adapter.py
  memory.py
  workflow.py
  cli.py

nanobot/agent/tools/lark_meeting.py
nanobot/skills/lark-meeting/SKILL.md
tests/meeting/
tests/fixtures/meeting/
scripts/lma-real
```

## Lark Boundary

`LarkToolAdapter` is the only meeting-domain boundary to Lark. Workflows, tools, analyzers, and skills do not call `lark-cli`, Lark HTTP APIs, or Lark SDKs directly.

The adapter has two providers:

1. `FakeLarkProvider` for CI and demos without credentials.
2. `CliLarkProvider` for local real dry-runs and approved writes through `lark-cli`.

The CLI provider builds argv arrays and uses `subprocess.run(..., shell=False)`. It parses JSON output and rejects malformed results.

## Analyzer Boundary

`MeetingAnalyzer` is a protocol. Fake mode is deterministic and test-only. LLM mode uses an OpenAI-compatible API and defaults to DeepSeek through environment variables:

```text
LMA_LLM_API_KEY or DEEPSEEK_API_KEY
LMA_LLM_BASE_URL
LMA_LLM_MODEL
```

Analyzer output is parsed into Pydantic schemas. Decisions and action items without evidence are rejected by schema validation.

## Approval Model

`process` never executes write operations. It returns a `WritePlan` with operation IDs and previews. `approve` loads the persisted run snapshot and executes only selected operation IDs. Missing targets, such as `im.send` without `chat_id`, remain skipped.

## Memory Model

The MVP persists structured meeting data in workspace-local `.lark_meeting_agent/` JSONL files. This is deliberately simple and reviewable. It can later be replaced or complemented by nanobot session memory or a vector index without changing the source-grounding contract.

## Real-mode Automation

`scripts/lma-real` loads the DeepSeek key from macOS Keychain service `lark-meeting-agent.deepseek-api-key`, verifies `lark-cli auth status --verify`, defaults `LARK_CLI_NO_PROXY=1`, and invokes the real CLI provider plus LLM analyzer. The script does not contain secrets.

## Security Notes

Meeting transcripts and fetched docs are untrusted input. Prompt instructions embedded inside meeting content do not trigger tool calls. Writes require explicit approval. Audit events redact common secrets and Lark tokens.
