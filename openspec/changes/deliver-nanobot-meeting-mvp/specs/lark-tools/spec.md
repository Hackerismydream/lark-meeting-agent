# Delta for Lark Tools

## ADDED Requirements

### Requirement: Implemented LarkToolAdapter Boundary

All meeting-domain Lark operations MUST go through `LarkToolAdapter`.

Workflows, analyzers, nanobot tool wrappers, and skills MUST NOT call `lark-cli`, Lark HTTP APIs, Lark SDKs, or `subprocess` directly for Lark operations.

#### Scenario: Real meeting read

- GIVEN the workflow needs meeting text from Lark
- WHEN provider mode is `cli`
- THEN the workflow calls `LarkToolAdapter`
- AND the adapter invokes the allowlisted CLI provider operation.

### Requirement: Fake and CLI Providers

The adapter MUST provide fake and CLI provider modes.

The fake provider MUST run without Lark credentials. The CLI provider MUST use JSON output, timeouts, argv arrays, `shell=False`, and typed errors for malformed output.

#### Scenario: Malformed CLI output

- GIVEN `lark-cli` returns malformed JSON
- WHEN the CLI provider parses the output
- THEN it raises a tool execution error
- AND records a failed audit event.

### Requirement: Implemented Operation Allowlist

The adapter MUST allow only MVP operations:

1. `auth.status`
2. `vc.search`
3. `vc.notes`
4. `docs.fetch`
5. `minutes.search`
6. `calendar.agenda`
7. `docs.create`
8. `task.create`
9. `im.send`

#### Scenario: Unknown operation rejected

- GIVEN an operation such as `drive.delete_file`
- WHEN the adapter is asked to execute it
- THEN it rejects the operation.

### Requirement: Approval-gated Writes

Write operations MUST require approval unless they are dry-run previews.

#### Scenario: Write without approval rejected

- GIVEN a write operation such as `docs.create`
- WHEN it is executed with `dry_run=false` and no approved status
- THEN the adapter raises `ApprovalRequiredError`.

### Requirement: Audit and Redaction

Every adapter call MUST append an audit event with sanitized input, provider mode, read/write classification, dry-run flag, approval status, execution status, and error/result summary.

Secrets MUST be redacted from audit inputs and errors.

#### Scenario: Token redaction

- GIVEN a payload or error contains a token-like secret
- WHEN it is recorded by the adapter
- THEN the stored audit text contains a redaction marker instead of the raw secret.
