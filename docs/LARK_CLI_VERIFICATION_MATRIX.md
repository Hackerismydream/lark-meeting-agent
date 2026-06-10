# Lark CLI Verification Matrix

Last updated: 2026-06-10

This matrix separates adapter implementation from real account verification. `implemented` means `LarkToolAdapter` has an allowlisted provider path. It does not imply the current Feishu account has readable data or that a real write was executed.

| Operation | CLI command template | Implemented in adapter | Fake test coverage | Real smoke status | Blockers / notes | Last verified |
| --- | --- | --- | --- | --- | --- | --- |
| `auth.status` | `lark-cli auth status --verify` | yes | indirect | verified | User and bot identities verify locally through `scripts/lma-real status`. | 2026-06-10 |
| `vc.search` | `lark-cli vc +search --format json --as user --query <query>` | yes | yes | verified | Current account can search visible VC meetings. | 2026-06-10 |
| `vc.notes` | `lark-cli vc +notes --format json --as user --meeting-ids <meeting_id>` | yes | yes | blocked | Command path is callable, but visible meetings currently return no notes, no minute file, or no permission to access minutes. | 2026-06-10 |
| `minutes.search` | `lark-cli minutes +search --format json --as user --query <query>` | yes | yes | blocked | Command path is callable, but current account has zero accessible minute records in checked ranges. | 2026-06-10 |
| `calendar.agenda` | `lark-cli calendar +agenda --format json --as user --query <query>` | yes | yes | unverified | Adapter argv exists; real command/flags still need direct smoke verification. | unverified |
| `docs.search` | `lark-cli docs +search --api-version v2 --format json --as user --query <query>` | yes | yes | unverified | Adapter argv exists; real command/flags still need direct smoke verification. | unverified |
| `docs.fetch` | `lark-cli docs +fetch --api-version v2 --format json --as user --doc <token>` | yes | yes | unverified | Adapter argv exists; requires a readable document token for real smoke. | unverified |
| `docs.create` dry-run | `lark-cli docs +create --api-version v2 --format json --as user --dry-run --title <title> --markdown <markdown>` | yes | yes | unverified | Write path is approval-gated; dry-run command/flags still need real smoke verification. | unverified |
| `task.create` dry-run | `lark-cli task +create --format json --as user --dry-run --summary <summary> --description <description>` | yes | yes | unverified | Write path is approval-gated; dry-run command/flags still need real smoke verification. | unverified |
| `im.send` dry-run | `lark-cli im +messages-send --format json --as user --dry-run --chat-id <chat_id> --markdown <markdown>` | yes | yes | unverified | Requires an explicit safe chat ID. No real send is claimed. | unverified |
| `task.search` / `task.list` | `lark-cli task +list --format json --as user --query <query> --status <status>` | yes | yes | unverified | Adapter argv exists; real command/flags still need direct smoke verification. | unverified |

## Current Real Gate

The remaining real meeting blocker is not local code execution. The current account can authenticate and search meetings, but it does not currently expose readable meeting notes/minutes transcript content to `vc.notes` or `minutes.search`. See `docs/BLOCKERS.md`.
