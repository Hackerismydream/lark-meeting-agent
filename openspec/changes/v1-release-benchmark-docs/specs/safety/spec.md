# Delta for Safety in V1 Release, Benchmark, and Docs

## ADDED Requirements

### Requirement: Safety Boundary for v1-release-benchmark-docs

The system MUST preserve existing enterprise collaboration safety constraints during `v1-release-benchmark-docs`.

#### Scenario: Approval boundary

- GIVEN a Lark write, meeting join, or meeting leave operation
- WHEN no explicit approval is present
- THEN the operation is rejected
- AND an audit event is recorded when applicable.

#### Scenario: Untrusted meeting content

- GIVEN transcript, chat, retrieved docs, simulated events, or shared content contain tool instructions
- WHEN the agent processes the content
- THEN the content is treated as data only
- AND no tool call or approval bypass is triggered.
