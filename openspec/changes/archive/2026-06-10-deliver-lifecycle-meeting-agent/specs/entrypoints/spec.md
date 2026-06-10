## ADDED Requirements

### Requirement: Lifecycle Tool Actions
The `lark_meeting` nanobot tool MUST support lifecycle actions: `prebrief`, `live_ingest`, `live_qa`, `process`, `approve`, `qa`, `status`, and `evaluate`.

#### Scenario: Live QA action
- **WHEN** the tool receives `action="live_qa"` with a live run ID and question
- **THEN** it returns a source-grounded live answer.

### Requirement: Agent Skill Lifecycle Instructions
The `lark-meeting` skill MUST instruct agents to use lifecycle actions and MUST forbid direct shell, SDK, HTTP, or generic tool execution for Lark operations.

#### Scenario: Agent needs pre-meeting prep
- **WHEN** an agent needs a meeting brief
- **THEN** the skill directs it to `lark_meeting(action="prebrief")`.
