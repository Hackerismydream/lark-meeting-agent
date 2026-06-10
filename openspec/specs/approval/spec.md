# Approval Spec

## Purpose

Define the approval protocol for meeting-agent write operations.

## Requirements

### Requirement: Approval prompt protocol
When a process run returns `approval_required`, the bot MUST render a prompt with run ID, summary, decisions, action items, write operations, approve instructions, reject instructions, and a no-writes-executed warning.

#### Scenario: Render approval prompt
- **WHEN** a process run generates a write plan
- **THEN** the bot response includes operation IDs and explicit `/meeting approve` and `/meeting reject` examples.

### Requirement: Selected operation approval
The bot MUST execute only explicitly approved operation IDs.

#### Scenario: Partial approval
- **WHEN** the approver approves only one operation ID
- **THEN** only that operation executes and unselected operations remain rejected or skipped.

### Requirement: Reject command
The bot MUST support rejecting all pending operations for a run.

#### Scenario: Reject run
- **WHEN** an approver sends `/meeting reject <run_id>`
- **THEN** pending operations are marked rejected and no Lark write executes.
