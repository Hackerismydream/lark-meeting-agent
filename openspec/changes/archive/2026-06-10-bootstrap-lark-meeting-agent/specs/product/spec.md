# Delta for Product

## ADDED Requirements

### Requirement: Product Scope

The system MUST be a Feishu/Lark-native meeting workflow agent based on HKUDS/nanobot v0.2.1.

It MUST support meeting-related workflows around:

1. meeting preparation,
2. meeting transcript processing,
3. structured meeting minutes,
4. decision extraction,
5. action item extraction,
6. Lark collaboration write planning,
7. long-term meeting memory,
8. cross-meeting source-grounded QA.

The MVP MUST focus on post-meeting processing only.

Feishu bot delivery SHOULD reuse nanobot's Feishu channel. Standalone FastAPI MUST NOT be the MVP core architecture.

#### Scenario: Post-meeting MVP flow

- GIVEN a user provides a completed meeting transcript
- WHEN the post-meeting workflow runs
- THEN the system generates structured meeting minutes
- AND extracts decisions, action items, risks, and open questions
- AND generates a dry-run write plan for Lark docs, tasks, and IM messages
- AND requires approval before executing any write operation.

#### Scenario: Feature outside MVP

- GIVEN a user requests realtime meeting bot participation
- WHEN the MVP is running
- THEN the system MUST return a clear unsupported-feature response
- AND MUST NOT attempt to join a live meeting.

#### Scenario: FastAPI standalone request outside MVP

- GIVEN a developer proposes building a standalone FastAPI service as the MVP core
- WHEN the OpenSpec is reviewed
- THEN the proposal is rejected or deferred
- AND the system remains based on nanobot runtime.

### Requirement: Non-goals

The MVP MUST NOT implement:

1. custom ASR,
2. realtime meeting bot,
3. production OAuth onboarding,
4. complex frontend dashboard,
5. arbitrary autonomous shell/tool calling,
6. production multi-tenant permissions,
7. vector database optimization,
8. independent Feishu channel runtime,
9. independent generic memory runtime,
10. independent WebUI or model-routing runtime.

#### Scenario: User uploads audio

- GIVEN a user uploads an audio file
- WHEN the MVP receives the request
- THEN the system MUST respond that custom ASR is not supported in MVP
- AND MAY suggest using an existing transcript input path.

### Requirement: Recruiting Project Demonstrability

The system MUST demonstrate practical Agent engineering capability.

It SHOULD emphasize:

1. nanobot extension reuse,
2. deterministic workflow orchestration,
3. safe tool execution,
4. schema validation,
5. evidence preservation,
6. fixture-based testing,
7. source-grounded QA.

#### Scenario: Demo execution without external credentials

- GIVEN a developer clones the repository
- WHEN they run tests and local demo with fake provider
- THEN the system works without real Lark credentials.
