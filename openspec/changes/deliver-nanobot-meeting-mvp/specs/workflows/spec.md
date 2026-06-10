# Delta for Workflows

## ADDED Requirements

### Requirement: Implemented PostMeetingWorkflow

The MVP MUST implement a deterministic `PostMeetingWorkflow`.

The workflow MUST support transcript-file processing and latest-ended meeting processing through the Lark adapter.

#### Scenario: Process transcript fixture

- GIVEN a transcript fixture
- WHEN `process` runs with fake provider and fake analyzer
- THEN the workflow normalizes, analyzes, builds a write plan, persists the run, and returns `approval_required` when write operations exist.

#### Scenario: Process latest ended meeting

- GIVEN provider mode is `cli`
- WHEN `process` runs with `latest_ended`
- THEN the workflow searches meetings, fetches notes or doc content, normalizes text, and analyzes it.

### Requirement: Process Never Executes Writes

The process workflow MUST NOT execute write operations.

#### Scenario: Dry-run write plan

- GIVEN create-doc or create-tasks options are enabled
- WHEN `process` completes
- THEN write operations remain pending
- AND no real Lark write is executed.

### Requirement: Approval Executes Selected Operations Only

The approve workflow MUST execute only selected operation IDs from a persisted run snapshot.

#### Scenario: Partial approval

- GIVEN a write plan contains multiple operations
- WHEN only one operation ID is approved
- THEN only that operation executes
- AND all unselected operations are skipped or rejected.

### Requirement: Run Persistence

Every workflow run MUST have a `run_id` and a persisted snapshot that can be loaded by approve and status paths.

#### Scenario: Load run for approval

- GIVEN a previous process run persisted a snapshot
- WHEN approve is called with the run ID
- THEN the workflow loads the run and updates operation results.
