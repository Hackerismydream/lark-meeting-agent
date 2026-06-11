## ADDED Requirements

### Requirement: Agent mode artifacts

Agent mode SHALL write per-fixture artifacts under the run directory.

#### Scenario: Fixture artifact set

- **WHEN** a fixture completes in agent mode
- **THEN** the fixture artifact directory SHALL contain `prebrief.md`, `prebrief_sources.json`, `live_state_snapshots.jsonl`, `live_qa_answers.jsonl`, `minutes.md`, `decisions.json`, `action_items.json`, `risks.json`, `open_questions.json`, `write_plan.json`, and `qa_answers.jsonl`
