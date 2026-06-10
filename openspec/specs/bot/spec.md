# Bot Spec

## Purpose

Define the production Feishu bot entrypoint for controlled meeting workflows.

## Requirements

### Requirement: Feishu bot entrypoint
The production bot MUST receive Feishu DM and group messages through nanobot's Feishu channel and route supported meeting commands to controlled meeting actions.

#### Scenario: Process command in DM
- **WHEN** an allowed user sends `/meeting process`
- **THEN** the bot routes to the post-meeting process action and returns a preview or blocker.

#### Scenario: Group requires command or mention
- **WHEN** a group message does not mention the bot and does not start with `/meeting`
- **THEN** the production bot ignores it.

### Requirement: Meeting command UX
The production bot MUST support deterministic commands for process, prebrief, approve, reject, status, and QA.

#### Scenario: QA command
- **WHEN** an allowed user sends `/meeting qa <question>`
- **THEN** the bot returns a source-grounded answer or insufficient evidence.

### Requirement: Natural language aliases
The production bot MUST map approved Chinese aliases such as `整理最近一场会` and `查看待审批操作` to deterministic commands.

#### Scenario: Alias process
- **WHEN** an allowed user sends `整理最近一场会，先不要写入飞书`
- **THEN** the bot maps it to a dry-run process request.
