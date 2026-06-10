# macOS Companion App Roadmap

The macOS app is not the primary agent runtime. It should be a companion client for the production Feishu bot and meeting knowledge service.

Do not implement the macOS app before the production Feishu bot path is stable.

## Product Role

The macOS app should provide:

1. menu bar meeting status,
2. pre-brief notifications,
3. WritePlan approval inbox,
4. run trace viewer,
5. cross-meeting search,
6. transcript/audio upload entry,
7. links to created Lark docs/tasks/meetings,
8. local notification and shortcut convenience.

It must not directly write to Lark. Writes still go through backend `LarkToolAdapter` and approval policy.

## Recommended Architecture

```text
macOS SwiftUI app
  -> local/remote Agent API
  -> production Feishu bot service
  -> Meeting workflows
  -> LarkToolAdapter
  -> Lark provider
```

## First Version Scope

- MenuBarExtra status.
- Approval inbox.
- Run trace viewer.
- Cross-meeting search.
- Open Lark doc/task links.

## Later Scope

- Transcript/audio upload.
- Local Agent Mode.
- Keychain-managed local secrets.
- Offline cache.
- Notification rules.

## Security Rules

- No direct Lark writes from the macOS app.
- Keychain for local secrets if Local Agent Mode is added.
- Explicit user confirmation for approvals.
- Audit all approval actions through backend.
- Respect backend access policy.
