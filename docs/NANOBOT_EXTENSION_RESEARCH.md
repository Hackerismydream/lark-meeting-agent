# Nanobot Extension Research

Research target: HKUDS/nanobot v0.2.1.

Import source: upstream tag `v0.2.1`, commit `f309982bb0a2dca76dd038473ee6f1be803bd503`.

## AgentLoop

`nanobot/agent/loop.py` owns the core runtime:

- receives inbound messages from `MessageBus`,
- restores session/history,
- dispatches commands through `CommandRouter`,
- builds context,
- calls the configured provider/model,
- executes registered tools,
- sends outbound messages.

Decision: do not modify `AgentLoop` for the MVP. The meeting feature is exposed as a normal nanobot tool and a local developer CLI.

## CommandRouter

`nanobot/command/router.py` supports:

- priority exact commands,
- exact commands,
- longest-prefix command routing.

Decision: `/meeting process`, `/meeting approve`, and `/meeting qa` are viable later command entrypoints. The MVP implements `lark_meeting` tool plus local CLI first, because that is less invasive.

## Tool, ToolRegistry, ToolLoader

`nanobot/agent/tools/base.py` defines `Tool` with:

- `name`,
- `description`,
- JSON Schema `parameters`,
- async `execute`.

`ToolRegistry` validates parameters before execution. `ToolLoader` discovers built-in tools by scanning `nanobot.agent.tools` modules and also supports `nanobot.tools` entry points.

Decision: add `nanobot/agent/tools/lark_meeting.py` as a built-in tool module. This avoids changes to core loader code.

## Feishu Channel

`nanobot/channels/feishu.py` already implements Feishu/Lark chat delivery using the Lark SDK and WebSocket long connection.

Relevant config from upstream docs:

- `appId`,
- `appSecret`,
- `allowFrom`,
- `groupPolicy`,
- `streaming`,
- `domain`.

Decision: do not modify Feishu channel for MVP. Real Feishu chat flow is documented as later integration over the `lark_meeting` tool/skill.

## Skills

Built-in skills live under `nanobot/skills/<skill-name>/SKILL.md`.

Decision: add `nanobot/skills/lark-meeting/SKILL.md` to tell nanobot when to use `lark_meeting`, when approval is required, and why exec/shell must not call `lark-cli`.

## Memory and Session

nanobot has session history and long-term Dream memory. Meeting knowledge has stricter structure requirements: decisions/action items must retain evidence refs.

Decision: use workspace-local `.lark_meeting_agent/*.jsonl` files for structured meeting memory. Do not replace nanobot generic memory.

## Provider and Model Routing

nanobot has provider/model routing, including OpenAI-compatible support. Reusing the provider layer directly would require more runtime wiring than the first MVP needs.

Decision: implement `OpenAICompatibleMeetingAnalyzer` behind the `MeetingAnalyzer` interface as a temporary minimal path. It reads:

- `LMA_LLM_API_KEY` or `DEEPSEEK_API_KEY`,
- `LMA_LLM_BASE_URL`, default `https://api.deepseek.com`,
- `LMA_LLM_MODEL`, default `deepseek-v4-pro`.

This is documented as temporary and can be replaced by deeper nanobot provider reuse later.

## Security and Workspace Settings

nanobot supports `tools.exec.enable`, `tools.restrictToWorkspace`, and exec sandbox settings.

Decision:

- the meeting workflow never calls nanobot exec/shell,
- real Lark commands are called only inside `LarkToolAdapter`,
- subprocess calls use argument lists with `shell=False`,
- production-like meeting-agent configs should disable exec unless explicitly needed.

## Test Structure

Upstream tests live under `tests/`. The MVP adds `tests/meeting/` and `tests/fixtures/meeting/`.

Decision: meeting tests use fake provider and fake analyzer only. Real Lark and real LLM tests are manual or must be opt-in via environment flags in future work.
