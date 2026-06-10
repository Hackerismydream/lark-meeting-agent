# Product Spec

## Purpose

Define product scope and positioning for Lark Meeting Agent.
## Requirements
### Requirement: Lifecycle Product Contract
The product MUST be described as a Lark meeting workflow agent covering pre-meeting, in-meeting, post-meeting, long-term memory, and cross-meeting QA.

#### Scenario: Product positioning
- **WHEN** documentation describes the lifecycle agent
- **THEN** it distinguishes implemented lifecycle workflows from non-goals such as custom ASR and automatic bot join.

### Requirement: Current Capability Honesty
Documentation MUST distinguish fake fixture validation, real DeepSeek validation, real lark-cli auth/search validation, and account-dependent real minutes availability.

#### Scenario: Real Lark blocker documented
- **WHEN** real Lark minutes are not readable for the current account
- **THEN** docs state that the code path is implemented but account data availability blocks transcript retrieval.

### Requirement: Lifecycle MVP truthfulness
Documentation MUST describe the current implementation as a lifecycle local MVP where post-meeting is the most complete closed-loop slice.

#### Scenario: Docs avoid overclaiming
- **WHEN** docs describe live meeting support
- **THEN** they state that live support consumes supplied transcript/event deltas and does not implement automatic bot join or custom ASR.

### Requirement: Fixture metrics are labeled
Documentation MUST label fixture metrics as fixture benchmark metrics, not production deployment metrics.

#### Scenario: Benchmark docs
- **WHEN** delivery docs mention precision or recall
- **THEN** they state the benchmark type and data source.

### Requirement: Phase ordering
The product roadmap MUST place production Feishu bot before macOS app implementation.

#### Scenario: Roadmap reader
- **WHEN** a reviewer reads the roadmap
- **THEN** they see macOS as a companion phase after bot service, storage, and approval protocol.
