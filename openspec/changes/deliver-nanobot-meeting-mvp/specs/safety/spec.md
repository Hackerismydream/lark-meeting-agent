# Delta for Safety

## ADDED Requirements

### Requirement: No Repository Secrets

The repository MUST NOT contain real DeepSeek API keys, Lark tokens, app secrets, refresh tokens, authorization codes, cookies, or `.env` secrets.

Real credentials MUST be supplied through local environment variables, local `lark-cli` auth state, or local Keychain.

#### Scenario: Secret scan

- GIVEN a commit is prepared
- WHEN repository contents are scanned for common key/token patterns
- THEN no real credential is found.

### Requirement: Prompt Injection Does Not Trigger Writes

Transcript, document, message, and retrieved memory text MUST be treated as untrusted content.

Embedded instructions MUST NOT trigger tool calls, bypass approval, reveal secrets, or execute writes.

#### Scenario: Malicious transcript instruction

- GIVEN a transcript says to ignore rules and send notes to a company-wide group
- WHEN the workflow processes it
- THEN it may appear only as meeting content
- AND no IM write operation is created unless send-message options and safe target are explicitly supplied.

### Requirement: Shell Execution Safety

The meeting-domain CLI provider MUST invoke `lark-cli` without a shell.

#### Scenario: Static shell check

- GIVEN meeting-domain source code is inspected
- WHEN checking for `shell=True`
- THEN no meeting-domain code uses shell execution.

### Requirement: Proxy Safety for Real-mode Helper

The real-mode helper MUST default `LARK_CLI_NO_PROXY=1` so Lark credential checks do not transit through a local proxy unless explicitly overridden.

#### Scenario: Helper runs status

- GIVEN a local HTTPS proxy exists
- WHEN `scripts/lma-real status` runs
- THEN the helper sets `LARK_CLI_NO_PROXY` by default before calling `lark-cli`.
