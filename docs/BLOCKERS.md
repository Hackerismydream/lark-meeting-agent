# Blockers

## Real Lark Read + Real LLM Dry-run Gate

Status: blocked by missing local Feishu/Lark user authorization.

The repository implementation, OpenSpec delivery change, fake CI gates, local real-mode helper, and `lark-cli` bot identity are in place. The remaining continuous MVP gate requires reading a real ended meeting through `lark-cli vc +search --as user`, but the local `lark-cli` user identity is not authorized.

Observed command:

```bash
LARK_CLI_NO_PROXY=1 lark-cli vc +search --format json --as user --query "项目例会"
```

Observed failure:

```text
identity: user
error.type: authentication
error.subtype: token_missing
message: need_user_authorization
required scope: vc:meeting.search:read
```

`lark-cli auth status --verify` confirms:

```text
bot identity: ready
user identity: missing
```

## Attempted Fixes

- Added `scripts/lma-real` to load the DeepSeek key from macOS Keychain and verify `lark-cli` auth.
- Set `LARK_CLI_NO_PROXY=1` in the helper before credential checks.
- Fixed `CliLarkProvider` to pass `--as user` for meeting read/write commands instead of relying on `defaultAs=auto`.
- Started split-flow authorization for scope `vc:meeting.search:read`.
- Generated QR-code authorization links for user authorization.
- Avoided committing authorization URLs, device codes, or secrets.

## Remaining Decision or Action Needed

The user must complete Feishu/Lark user authorization for:

```text
vc:meeting.search:read
```

After authorization, continue with:

```bash
LARK_CLI_NO_PROXY=1 lark-cli auth login --device-code <fresh_device_code>
scripts/lma-real process --latest-ended --query "项目例会" --create-doc --create-tasks --dry-run
```

If the prior device code expired, generate a fresh one:

```bash
LARK_CLI_NO_PROXY=1 lark-cli auth login --scope "vc:meeting.search:read" --no-wait --json
```

Then generate and show the QR code with:

```bash
lark-cli auth qrcode <verification_url> --output lma_lark_auth_qr.png
```

## Safest Next Prompt

After completing the Feishu authorization, tell Codex:

```text
已授权完成，继续真实 Lark dry-run gate
```

Codex should then finish device-flow polling, run the real dry-run, update `openspec/changes/deliver-nanobot-meeting-mvp/tasks.md`, commit the evidence update, and push the branch.
