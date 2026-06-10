# Implementation Notes

## Nanobot Import

Imported HKUDS/nanobot v0.2.1 source into the repository root.

Source tag:

```text
v0.2.1
```

Resolved upstream commit:

```text
f309982bb0a2dca76dd038473ee6f1be803bd503
```

Preserved Lark Meeting Agent files:

- `AGENTS.md`
- `README.md`
- `docs/`
- `openspec/`
- `.codex/`

Stored upstream references:

- `docs/NANOBOT_UPSTREAM_README.md`
- `docs/NANOBOT_UPSTREAM_AGENTS.md`
- `docs/nanobot-upstream/`

Imported upstream runtime/project files include:

- `nanobot/`
- `pyproject.toml`
- `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `SECURITY.md`
- `webui/`
- `bridge/`
- upstream tests and support files.

## Meeting MVP Implementation

Added:

- `nanobot/meeting/`
- `nanobot/agent/tools/lark_meeting.py`
- `nanobot/skills/lark-meeting/SKILL.md`
- `tests/meeting/`
- `tests/fixtures/meeting/`

The meeting workflow is deterministic. The LLM analyzer only produces structured meeting intelligence; it cannot execute tools or writes.

## LLM Provider

The real analyzer uses a minimal OpenAI-compatible path behind `MeetingAnalyzer`.

Default provider settings are DeepSeek-compatible:

```bash
export LMA_LLM_BASE_URL="https://api.deepseek.com"
export LMA_LLM_MODEL="deepseek-v4-pro"
export LMA_LLM_API_KEY="..."
```

`DEEPSEEK_API_KEY` is also accepted as a fallback.

No real key is committed. Do not put secrets in `.env`, fixtures, tests, logs, docs, or commits.

This is a temporary MVP integration. A later change can route through nanobot provider/model config after the product slice is stable.

## Lark CLI Provider

Local `lark-cli` version observed:

```text
lark-cli version 1.0.46
```

Confirmed command surfaces:

- `lark-cli vc +search --format json --query ...`
- `lark-cli vc +notes --format json --meeting-ids ...`
- `lark-cli docs +fetch --api-version v2 --format json --doc ...`
- `lark-cli docs +create --api-version v2 --format json --title ... --markdown ...`
- `lark-cli task +create --format json --summary ... --description ...`
- `lark-cli im +messages-send --format json --chat-id ... --markdown ...`

All real Lark operations go through `LarkToolAdapter`.

Subprocess rules:

- `shell=False`,
- argument lists only,
- timeout required,
- JSON output required,
- allowlist enforced,
- writes require approval.

## Known Limitations

- Feishu chat command registration is documented but not required for first MVP acceptance.
- Real LLM calls were not run during automated tests.
- Real Lark writes were not run during automated tests.
- Owner-to-open_id mapping is intentionally not implemented. Unknown assignees remain unassigned or in task description.
- IM send is supported by adapter but should remain dry-run unless a safe `chat_id` is provided and explicitly approved.

## Lint Baseline

The imported nanobot v0.2.1 tree contains existing style patterns that fail the default `ruff` rule set in this repository, mostly import sorting, module-level import placement, naming style, semicolon style, and unused variables in upstream tests.

`pyproject.toml` keeps critical lint checks enabled but ignores those upstream baseline style rules so the required command can run across the imported tree:

```bash
ruff check nanobot tests
```

New meeting code was also checked directly with:

```bash
ruff check nanobot/meeting nanobot/agent/tools/lark_meeting.py tests/meeting
```
