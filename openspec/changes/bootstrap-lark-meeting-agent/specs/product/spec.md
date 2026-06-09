# Delta for Product

## ADDED Requirements

### Requirement: Product Scope

The system MUST be a Feishu/Lark-native meeting workflow agent.

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

### Requirement: Non-goals

The MVP MUST NOT implement:

1. custom ASR,
2. realtime meeting bot,
3. production OAuth onboarding,
4. complex frontend dashboard,
5. arbitrary autonomous shell/tool calling,
6. production multi-tenant permissions,
7. vector database optimization.

#### Scenario: User uploads audio

- GIVEN a user uploads an audio file
- WHEN the MVP receives the request
- THEN the system MUST respond that custom ASR is not supported in MVP
- AND MAY suggest using an existing transcript input path.

### Requirement: Recruiting Project Demonstrability

The system MUST demonstrate practical Agent engineering capability.

It SHOULD emphasize:

1. deterministic workflow orchestration,
2. safe tool execution,
3. schema validation,
4. evidence preservation,
5. fixture-based testing,
6. source-grounded QA.

#### Scenario: Demo execution without external credentials

- GIVEN a developer clones the repository
- WHEN they run tests and local demo with fake provider
- THEN the system works without real Lark credentials.
