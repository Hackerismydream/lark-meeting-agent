# Delta for Product

## ADDED Requirements

### Requirement: Nanobot-based Post-meeting MVP

The system MUST deliver the Lark Meeting Agent MVP as a meeting-domain extension inside HKUDS/nanobot v0.2.1.

The MVP MUST process completed meeting transcripts or fetched Lark meeting notes, generate structured minutes, prepare Lark write plans, persist meeting knowledge, and answer historical questions with sources.

The MVP MUST NOT use a standalone FastAPI app, independent Feishu bot runtime, independent generic agent loop, custom ASR, or vector database as the core runtime.

#### Scenario: Fake vertical slice works without credentials

- GIVEN a transcript fixture
- WHEN the post-meeting workflow runs with fake provider and fake analyzer
- THEN it returns structured minutes
- AND returns evidence-linked decisions and action items
- AND returns a dry-run write plan
- AND persists meeting memory.

#### Scenario: Real dry-run does not write

- GIVEN local `lark-cli` auth and a real LLM key are configured
- WHEN the workflow runs with CLI provider and LLM analyzer in dry-run mode
- THEN it fetches real meeting text
- AND returns structured minutes and a write plan
- AND does not create docs, tasks, or messages.

### Requirement: Demonstrable Real-mode Helper

The repository MUST provide a local helper for real-mode operation that does not store secrets in the repository.

#### Scenario: Helper status check

- GIVEN the DeepSeek key is stored in the local Keychain
- AND `lark-cli` is authenticated
- WHEN `scripts/lma-real status` is executed
- THEN the helper verifies real-mode prerequisites without printing secrets.
