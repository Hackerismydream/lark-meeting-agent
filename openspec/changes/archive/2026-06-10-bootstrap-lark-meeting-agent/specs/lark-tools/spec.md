# Delta for Lark Tools

## ADDED Requirements

### Requirement: Single Lark Tool Boundary

All Lark-related operations MUST go through `LarkToolAdapter`.

nanobot tools, commands, skills, workflows, analyzers, and channel handlers MUST NOT call `subprocess`, `lark-cli`, Lark HTTP APIs, or Lark SDKs directly.

nanobot's general exec/shell tool MUST NOT be used for Lark operations.

#### Scenario: Workflow needs transcript

- GIVEN a workflow needs transcript data
- WHEN it interacts with Lark-related data
- THEN it calls `LarkToolAdapter`
- AND does not call `lark-cli` directly.

#### Scenario: Direct lark-cli via nanobot exec blocked

- GIVEN a model or user asks nanobot's exec tool to run `lark-cli`
- WHEN the command is related to Lark operations
- THEN the command is blocked by policy
- AND the workflow is told to use `LarkToolAdapter`.

### Requirement: Provider Modes

The adapter MUST support at least two provider modes:

1. `fake`
2. `cli`

The fake provider MUST be the default mode for tests.

The CLI provider is later scope and MUST be allowlisted, audited, timeout-controlled, secret-redacted, and approval-gated.

#### Scenario: Tests without credentials

- GIVEN tests run without Lark credentials
- WHEN the provider mode is fake
- THEN the adapter returns fixture-based responses
- AND no external command or network call is executed.

### Requirement: Allowlisted Operations

The adapter MUST maintain an allowlist of supported operations.

MVP allowlist:

1. `auth.status`
2. `vc.search`
3. `vc.notes`
4. `docs.fetch`
5. `minutes.search`
6. `calendar.agenda`
7. `docs.create`
8. `task.create`
9. `im.send`

Any operation not in the allowlist MUST be rejected.

#### Scenario: Unknown operation

- GIVEN an agent requests `drive.delete_file`
- WHEN the operation is not allowlisted
- THEN the adapter rejects the operation
- AND records a rejected tool call audit event.

### Requirement: Read and Write Separation

The adapter MUST classify operations as read or write.

Read operations MAY execute automatically.

Write operations MUST require:

1. dry-run preview,
2. explicit approval,
3. audit event.

#### Scenario: Create Lark tasks

- GIVEN extracted action items
- WHEN the workflow wants to create Lark tasks
- THEN the adapter MUST first return a dry-run preview
- AND MUST NOT execute the write until approval is granted.

### Requirement: Structured Output

The CLI provider MUST request and parse structured output.

The system SHOULD prefer JSON output when available.

Human-readable table output MUST NOT be used as the primary integration contract.

All Lark tool inputs and parsed outputs MUST be validated by typed schemas before they cross the adapter boundary.

#### Scenario: CLI output parsing

- GIVEN a CLI operation returns JSON
- WHEN the adapter parses the result
- THEN it validates the output against the expected schema.

#### Scenario: Malformed CLI output

- GIVEN a CLI operation returns malformed structured output
- WHEN the adapter parses the result
- THEN it rejects the result with a typed tool execution error
- AND records a failed audit event.

### Requirement: Tool Call Audit

Every tool call MUST produce an audit record.

Audit records MUST include operation name, sanitized input parameters, provider mode, read/write classification, dry-run flag, approval status, execution status, exit code when applicable, parsed result summary, error message when applicable, and timestamp.

#### Scenario: Failed tool execution

- GIVEN a CLI operation fails
- WHEN the adapter catches the failure
- THEN it records a failed audit event
- AND returns a typed tool execution error.
