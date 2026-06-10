# Production Feishu Bot Deployment

This document defines the target deployment path for turning Lark Meeting Agent from a lifecycle local MVP into a production Feishu bot.

Current status: documentation/spec stage. Do not claim production deployment until a real Feishu app has been configured and smoke-tested.

## Production Bar

A production Feishu bot must:

1. receive Feishu DM/group messages through nanobot Feishu channel,
2. enforce user and group access policy,
3. route meeting commands to controlled `lark_meeting` actions,
4. return WritePlan previews before writes,
5. accept explicit approval or rejection commands,
6. execute only approved write operations,
7. persist runs, write operations, approval state, audit events, and memory records,
8. expose deployment config and safety checklist,
9. keep Lark operations behind `LarkToolAdapter`,
10. keep real tests opt-in and secrets out of repo files.

## Feishu App Setup

Create a Feishu/Lark app with bot capability enabled.

Required production setup:

- App ID and app secret stored outside the repo.
- Bot enabled.
- Event subscription enabled.
- Long Connection mode preferred for early deployment because it avoids a public HTTPS callback endpoint.
- Message receive event enabled.
- User/group access limited by nanobot channel config and meeting-agent access policy.

Minimum scopes depend on enabled workflows. Current target scopes:

- `im:message`
- `im:message.p2p_msg:readonly`
- `im:message.group_msg:get_as_user`
- `im:message.send_as_user`
- `vc:meeting.search:read`
- `vc:note:read`
- `vc:meeting.meetingevent:read`
- `vc:record:readonly`
- `minutes:minutes.search:read`
- `docs:document.content:read`
- `docx:document:create`
- `task` creation/read scopes according to tenant setup

Verify exact Feishu scope names in the app console before production rollout.

## Nanobot Config Shape

Use environment variable placeholders for secrets:

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "${FEISHU_APP_ID}",
      "appSecret": "${FEISHU_APP_SECRET}",
      "allowFrom": ["ou_allowed_user"],
      "groupPolicy": "mention",
      "streaming": true
    }
  },
  "tools": {
    "exec": {
      "enable": false
    },
    "restrictToWorkspace": true
  }
}
```

Production must not use wildcard `allowFrom` unless explicitly intended and documented.

## Meeting Agent Config

The implementation phase should add meeting-agent config for:

- allowed users,
- allowed chat IDs,
- admin users,
- write approvers,
- dry-run default,
- global writes enabled/disabled,
- provider mode,
- storage backend,
- audit settings.

## Startup

Target startup command:

```bash
nanobot gateway
```

Local development and diagnostics can still use:

```bash
scripts/lma-real status
uv run python -m nanobot.meeting.cli process --transcript-file tests/fixtures/meeting/transcripts/sample_project_sync.txt --provider-mode fake --analyzer-mode fake --create-doc --create-tasks --dry-run
```

## Production Provider Status

Current code has:

- `FakeLarkProvider` for CI/tests,
- `CliLarkProvider` for local diagnostics and demos.

Production target:

- `OapiLarkProvider` using Feishu/Lark OpenAPI credentials behind the same `LarkToolAdapter`.

`OapiLarkProvider` exists as a thin HTTP provider boundary. Until a real Feishu app, token lifecycle, scopes, and end-to-end smoke are verified, production deployment remains a target architecture, not a completed claim.

## Deployment Verification

Before claiming production deployment:

1. `nanobot gateway` starts with Feishu channel enabled.
2. Allowed DM sends `/meeting status` and receives a response.
3. Denied user is rejected.
4. Group message without mention/command is ignored.
5. `/meeting process` returns a WritePlan preview.
6. `/meeting approve <run_id> <operation_id>` works only for approvers.
7. `/meeting reject <run_id>` rejects pending operations.
8. Writes remain disabled or dry-run until human approval.
9. Audit events are persisted.
10. Real transcript gate is either passed or documented as blocked by account data.
