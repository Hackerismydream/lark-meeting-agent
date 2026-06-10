## Context

Current main is a lifecycle local MVP:

- Post-meeting is the most complete closed-loop workflow.
- Pre-brief and live workflows exist for controlled input and local/fake paths.
- `LarkToolAdapter` already enforces allowlist, dry-run, approval, provider binding, idempotency, audit, and redaction.
- Real lark-cli auth/search is connected, but real transcript/minutes access is blocked by account data.

The next step is not a macOS app. It is a production Feishu bot path that can use nanobot's Feishu channel and existing meeting workflows safely.

## Goals / Non-Goals

**Goals:**

- Define the production Feishu bot architecture and acceptance bar.
- Define command UX for DM/group meeting workflows.
- Define access policy and approver policy.
- Define persistent repositories and SQLite production MVP storage.
- Define approval prompt protocol and rejection protocol.
- Define provider strategy from fake/CLI to future OpenAPI.
- Define deployment docs and real transcript gate process.

**Non-Goals:**

- No custom ASR.
- No automatic meeting bot join.
- No macOS app implementation.
- No unapproved writes.
- No direct Lark API/CLI access outside `LarkToolAdapter`.
- No PostgreSQL in the first production MVP implementation.
- No real production deployment claim until a real Feishu app is configured and smoke-tested.

## Decisions

### Decision: Production bot first, macOS later

The production Feishu bot is the product core. A macOS app should later act as a companion control surface for approvals, traces, search, upload, and reminders. Building macOS first would produce a shell without production meeting infrastructure.

### Decision: Keep deterministic workflows behind message routing

Feishu messages route into deterministic `lark_meeting` actions. The LLM does not get free-form Lark tool access. This preserves the current safety model and keeps approval flows reviewable.

### Decision: Add repository abstraction before production storage

Production state requires durable runs, operations, approvals, and audit events. JSONL remains local/dev; SQLite becomes the production MVP backend behind repository interfaces. PostgreSQL can follow once the repository contract is stable.

### Decision: Treat CLI provider as diagnostic, not final production provider

`CliLarkProvider` is useful for local real smoke and demos. Production should move toward `OapiLarkProvider` using Feishu/Lark OpenAPI credentials and token lifecycles while preserving `LarkToolAdapter` as the boundary.

### Decision: Approval is a bot protocol, not an implicit chat reply

Approval prompts include run ID, operation IDs, preview text, and explicit approve/reject commands. Group approvals require approver authorization. No natural-language approval is accepted unless parsed into an explicit approved operation list.

## Architecture

```text
Feishu DM / group message
  -> nanobot Feishu channel
  -> Bot message router
  -> Meeting command parser
  -> Access policy
  -> lark_meeting action
      -> PreBriefWorkflow
      -> PostMeetingWorkflow
      -> Memory/QA
      -> ApprovalWorkflow
  -> Meeting repositories
      -> JSONL local backend
      -> SQLite production MVP backend
  -> LarkToolAdapter
      -> FakeLarkProvider
      -> CliLarkProvider
      -> OapiLarkProvider target
```

## Risks / Trade-offs

- [Risk] lark-cli dependence weakens production story. -> Mitigation: keep CLI as diagnostic provider and define `OapiLarkProvider` as production direction.
- [Risk] Feishu group messages can trigger unintended writes. -> Mitigation: group commands require mention/command and approval requires write approver membership.
- [Risk] SQLite may not scale to larger teams. -> Mitigation: use repository abstraction and document PostgreSQL as later backend.
- [Risk] real transcript access remains blocked. -> Mitigation: add transcript gate docs/helper and keep blocker separate from bot architecture.

## Migration Plan

1. Land this documentation/spec change.
2. Implement production command parser and approval renderer with fake tests.
3. Add access policy layer.
4. Add repository interfaces and SQLite backend.
5. Add deployment docs and production config validation.
6. Add optional real smoke for transcript access and write dry-runs.
