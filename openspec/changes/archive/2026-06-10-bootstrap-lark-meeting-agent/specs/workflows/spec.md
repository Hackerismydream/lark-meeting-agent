# Delta for Workflows

## ADDED Requirements

### Requirement: Explicit Workflow State Machine

The system MUST implement meeting workflows as explicit deterministic state machines inside the nanobot meeting domain module.

Each workflow MUST define input schema, state schema, ordered nodes, terminal states, error states, and emitted events.

nanobot AgentLoop MAY route user messages to meeting entrypoints, but MUST NOT replace PostMeetingWorkflow with a free-form autonomous loop.

#### Scenario: Workflow inspection

- GIVEN a workflow implementation
- WHEN a developer reads the workflow definition
- THEN they can identify each node and its input/output state.

### Requirement: PostMeetingWorkflow

The MVP MUST implement `PostMeetingWorkflow`.

It MUST execute the following nodes:

1. ResolveMeeting
2. FetchTranscript
3. NormalizeTranscript
4. AnalyzeMeeting
5. BuildWritePlan
6. RequestApproval
7. ExecuteApprovedWrites
8. PersistKnowledge
9. ReturnResult

#### Scenario: Successful dry-run

- GIVEN a completed meeting transcript
- WHEN the workflow runs with write options enabled
- THEN it generates meeting minutes
- AND builds a write plan
- AND returns `approval_required`
- AND executes no write operations before approval.

#### Scenario: Missing transcript

- GIVEN a meeting has no transcript
- WHEN the workflow reaches FetchTranscript
- THEN the workflow fails with `TranscriptNotFoundError`
- AND does not generate unsupported meeting content.

#### Scenario: Malformed transcript

- GIVEN a meeting transcript cannot be normalized
- WHEN the workflow reaches NormalizeTranscript
- THEN the workflow fails with `TranscriptNormalizationError`
- AND no write plan is generated.

#### Scenario: Analyzer output without evidence

- GIVEN analyzer output lacks evidence for decisions or action items
- WHEN the workflow validates analysis output
- THEN unsupported items are rejected or marked incomplete
- AND they are not used for confirmed writes.

#### Scenario: User rejects writes

- GIVEN a workflow generated a write plan
- WHEN the user rejects approval
- THEN no write operation is executed
- AND the generated minutes remain available locally.

#### Scenario: User approves selected writes

- GIVEN a workflow generated multiple write operations
- WHEN the user approves a subset
- THEN only approved operations are executed
- AND unapproved operations remain pending or skipped.

### Requirement: Workflow Run Tracking

Each workflow execution MUST have a `run_id`.

The system MUST store or expose run status.

Run status SHOULD include pending, running, approval_required, completed, failed, and rejected.

#### Scenario: Check run status

- GIVEN a workflow run was created
- WHEN the user requests run status
- THEN the system returns the current status and relevant outputs.

### Requirement: PreBriefWorkflow Contract

The system MUST define a later PreBriefWorkflow contract.

It SHOULD execute ResolveUpcomingMeeting, ClassifyMeetingType, RetrieveRelatedHistory, RetrieveOpenLoops, GeneratePreBrief, and ReturnBrief.

The MVP MAY defer implementation.

#### Scenario: Pre-brief not implemented

- GIVEN the MVP does not implement pre-brief yet
- WHEN a user requests pre-brief
- THEN the system returns a clear not-implemented response.
