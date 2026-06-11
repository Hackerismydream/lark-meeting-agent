# macOS Security

The macOS app is a companion client for the backend Agent Service. It must not become a second Agent runtime and must not call Lark APIs directly.

## Boundaries

- Lark reads and writes remain backend responsibilities.
- All write execution still goes through backend approval policy and `LarkToolAdapter`.
- The app only calls the Companion API.
- Approval requests must include explicit operation IDs.
- Transcript, document, chat, trace, and search content are treated as untrusted display/input data.

## Secrets

- Bearer tokens are loaded through `CredentialStore`.
- Persistent bearer tokens use macOS Keychain Services through `KeychainCredentialStore`.
- API base URL, environment label, and notification preference may be stored in `UserDefaults`.
- Tokens, cookies, Lark credentials, DeepSeek keys, `.env` contents, authorization codes, and private Feishu URLs must not be written to logs, docs, fixtures, screenshots, or release notes.

## Production Warning

The settings view displays a warning when the environment label contains `prod`. Production mode means backend-approved writes may affect real collaboration systems after backend confirmation.

## Local Security Checklist

- [x] Token storage uses Keychain abstraction.
- [x] UserDefaults stores only non-sensitive settings.
- [x] The Swift app has no `lark-cli` execution path.
- [x] The Swift app has no direct Lark HTTP or SDK path.
- [x] Approvals call backend Companion API only.
- [x] Upload supports text transcript files only.
- [x] No ASR or audio processing is claimed.
- [x] Signing and notarization are not claimed as complete.

## Residual Risks

- The current Swift package is a local development shell, not a hardened distributed `.app` bundle.
- Full macOS entitlement review requires a real Xcode project or packaging target.
- Notification permission behavior should be manually verified on a real desktop session.
