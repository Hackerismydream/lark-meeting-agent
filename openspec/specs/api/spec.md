# Api Spec

## Purpose

Define external and tool-facing API contracts for the meeting agent.

## Requirements

### Requirement: Nanobot Meeting Entrypoints
The MVP MUST expose meeting workflow entrypoints through nanobot chat/tool/command surfaces rather than a standalone FastAPI service as the primary interface.

Conceptual command entrypoints SHOULD include:

```text
/meeting process
/meeting approve
/meeting qa
```

If command registration is not selected after nanobot extension-point research, an equivalent controlled tool contract MUST be supported:

```text
lark_meeting(action="process")
lark_meeting(action="approve")
lark_meeting(action="qa")
```

Standalone REST/OpenAI-compatible API integration MAY be added in future scope.

#### Scenario: Process transcript fixture
- **GIVEN** a request references a transcript fixture
- **WHEN** `/meeting process` or `lark_meeting(action="process")` is invoked
- **THEN** it returns a run_id
- **AND** returns structured minutes
- **AND** returns a dry-run write plan when write options are enabled.

### Requirement: Entrypoint Schema Validation
The system MUST validate all external entrypoint inputs and outputs with typed Pydantic schemas.

Schema validation failures MUST return explicit validation errors instead of partially processed workflow results.

#### Scenario: Invalid entrypoint input
- **GIVEN** a process request omits the meeting reference or transcript fixture
- **WHEN** the meeting entrypoint receives the request
- **THEN** the request is rejected with a validation error
- **AND** no workflow run is created.

### Requirement: Approval Entrypoint
The system MUST expose an entrypoint to approve selected write operations.

The approval request and response MUST be validated by typed Pydantic schemas.

#### Scenario: Approve selected operations
- **GIVEN** a run is in `approval_required` state
- **WHEN** the user approves selected operation IDs through `/meeting approve` or an equivalent tool action
- **THEN** only selected operations are executed.

### Requirement: Run Inspection Entrypoint
The system MUST expose an entrypoint to inspect run status.

The run status response MUST be validated by a typed Pydantic schema.

#### Scenario: Inspect run
- **GIVEN** a workflow run exists
- **WHEN** the user requests the run status
- **THEN** the system returns status, minutes, write plan, and execution results.

### Requirement: Cross-meeting QA Entrypoint
The system MUST expose an entrypoint for source-grounded QA.

The QA request and response MUST be validated by typed Pydantic schemas.

Response MUST include answer, sources, and confidence or sufficiency flag.

#### Scenario: QA with sources
- **GIVEN** stored meeting knowledge contains relevant evidence
- **WHEN** the user asks a historical question through `/meeting qa` or an equivalent tool action
- **THEN** the answer includes source references.

#### Scenario: QA without evidence
- **GIVEN** no relevant evidence exists
- **WHEN** the user asks a question
- **THEN** the system returns insufficient evidence instead of hallucinating.
