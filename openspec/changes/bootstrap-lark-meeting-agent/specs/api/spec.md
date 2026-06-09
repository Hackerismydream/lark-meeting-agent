# Delta for API

## ADDED Requirements

### Requirement: Health Check

The system MUST expose a health check endpoint.

Endpoint:

```text
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

#### Scenario: Service health

- GIVEN the service is running
- WHEN a client calls `GET /health`
- THEN the response status is 200
- AND the body contains `"status": "ok"`.

### Requirement: Process Meeting Endpoint

The system MUST expose an endpoint for post-meeting processing.

All request and response payloads for this endpoint MUST be validated by typed Pydantic schemas.

Endpoint:

```text
POST /api/meetings/process
```

Request:

```json
{
  "meeting_ref": {
    "type": "latest_ended | meeting_id | calendar_event_id | transcript_file",
    "value": "string"
  },
  "options": {
    "dry_run": true,
    "create_doc": true,
    "create_tasks": true,
    "send_message": false
  }
}
```

Response MUST include run_id, status, minutes when available, write_plan when available, and errors when failed.

#### Scenario: Process transcript fixture

- GIVEN a request references a transcript fixture
- WHEN the endpoint is called
- THEN it returns a run_id
- AND returns structured minutes
- AND returns a dry-run write plan when write options are enabled.

### Requirement: Approve Run Endpoint

The system MUST expose an endpoint to approve write operations.

The approval request and approval response MUST be validated by typed Pydantic schemas.

Endpoint:

```text
POST /api/runs/{run_id}/approve
```

Request:

```json
{
  "approved_operation_ids": ["string"]
}
```

#### Scenario: Approve selected operations

- GIVEN a run is in `approval_required` state
- WHEN the user approves selected operation IDs
- THEN only selected operations are executed.

### Requirement: Get Run Endpoint

The system MUST expose an endpoint to inspect run status.

The run status response MUST be validated by a typed Pydantic schema.

Endpoint:

```text
GET /api/runs/{run_id}
```

#### Scenario: Inspect run

- GIVEN a workflow run exists
- WHEN the client requests the run
- THEN the system returns status, minutes, write plan, and execution results.

### Requirement: Cross-meeting QA Endpoint

The system MUST expose an endpoint for source-grounded QA.

The QA request and response MUST be validated by typed Pydantic schemas.

Endpoint:

```text
POST /api/qa
```

Request:

```json
{
  "question": "string",
  "filters": {
    "project": "string",
    "customer": "string",
    "date_range": ["YYYY-MM-DD", "YYYY-MM-DD"]
  }
}
```

Response MUST include answer, sources, and confidence or sufficiency flag.

#### Scenario: QA with sources

- GIVEN stored meeting knowledge contains relevant evidence
- WHEN the user asks a historical question
- THEN the answer includes source references.

#### Scenario: QA without evidence

- GIVEN no relevant evidence exists
- WHEN the user asks a question
- THEN the system returns insufficient evidence instead of hallucinating.

### Requirement: API Schema Validation

The system MUST validate all external API inputs and API responses with typed Pydantic schemas.

Schema validation failures MUST return explicit validation errors instead of partially processed workflow results.

#### Scenario: Invalid process request

- GIVEN a process meeting request omits `meeting_ref`
- WHEN the API receives the request
- THEN the request is rejected with a validation error
- AND no workflow run is created.
