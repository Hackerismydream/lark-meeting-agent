## ADDED Requirements

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
