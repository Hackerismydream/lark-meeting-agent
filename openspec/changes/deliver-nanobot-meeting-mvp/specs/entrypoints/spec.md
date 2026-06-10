# Delta for Entrypoints

## ADDED Requirements

### Requirement: Implemented Nanobot Tool Entrypoint

The MVP MUST expose a controlled nanobot tool named `lark_meeting`.

The tool MUST support actions:

1. `process`
2. `approve`
3. `qa`
4. `status`

#### Scenario: Tool process action

- GIVEN the tool receives `action="process"` and a transcript-file reference
- WHEN it executes
- THEN it calls `PostMeetingWorkflow`
- AND returns a serialized process result.

#### Scenario: Tool QA action

- GIVEN meeting memory contains relevant evidence
- WHEN the tool receives `action="qa"`
- THEN it returns a serialized QA answer with sources.

### Requirement: Agent-facing Skill

The MVP MUST include `nanobot/skills/lark-meeting/SKILL.md`.

The skill MUST instruct agents to use the controlled meeting tool/workflow and not direct shell or exec calls for Lark operations.

#### Scenario: Agent needs meeting workflow

- GIVEN an agent needs to process a meeting
- WHEN it reads the skill
- THEN it is directed to the meeting tool and approval-gated workflow.
