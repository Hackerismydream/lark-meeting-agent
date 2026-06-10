## Why

The project has a lifecycle local MVP, but it is not yet a production Feishu bot. The next product milestone is a deployable Feishu bot that receives real DM/group messages, enforces access policy, routes meeting commands, persists run state, renders approval prompts, and executes only approved writes.

This change defines the production bot track before implementation so the project does not drift into a macOS shell or another local-only demo.

## What Changes

- Define production Feishu bot entrypoints through nanobot Feishu channel.
- Define DM/group command UX for meeting processing, pre-briefs, QA, approval, rejection, and status.
- Define meeting-agent access control layered on top of nanobot Feishu channel controls.
- Define approval message protocol for WritePlan previews and selected operation approval.
- Define persistent run/write/audit/memory storage with JSONL retained for local/dev and SQLite as production MVP backend.
- Define Lark provider strategy: fake for CI, CLI for local diagnostics, OpenAPI provider as production direction.
- Define production deployment, security checklist, runbook, env template, and transcript gate docs.
- Keep macOS app out of this change except as separate companion roadmap documentation.

## Capabilities

### New Capabilities

- `bot`: Feishu bot entrypoints, command UX, and message routing.
- `storage`: Production run/write/audit persistence contract.
- `approval`: Bot-friendly WritePlan approval and rejection protocol.
- `deployment`: Production deployment, environment, runbook, and safety checklist.
- `lark-provider`: Provider strategy for fake, CLI, and future OpenAPI-backed production provider.

### Modified Capabilities

- `product`: Reposition next milestone from lifecycle local MVP to production Feishu bot.
- `safety`: Add production bot access policy, approver policy, and deployment safety gates.
- `lark-tools`: Preserve `LarkToolAdapter` as the only Lark boundary while clarifying provider roles.
- `workflows`: Route bot messages into existing deterministic meeting workflows.
- `memory`: Move production run state behind repositories while preserving JSONL local behavior.

## Impact

- Documentation and OpenSpec only in the first pass.
- Future implementation will affect `nanobot/channels/feishu.py` integration paths, `nanobot/command/`, `nanobot/meeting/`, `nanobot/agent/tools/lark_meeting.py`, tests, and deployment docs.
- No secrets, credentials, or real Feishu write actions are introduced by this documentation change.
