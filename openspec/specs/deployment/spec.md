# Deployment Spec

## Purpose

Define production deployment documentation and operational gates for the meeting agent.

## Requirements

### Requirement: Production deployment docs
The repository MUST document Feishu app setup, scopes, event subscription, long connection mode, nanobot config, provider config, storage config, secrets handling, startup, health checks, and common errors.

#### Scenario: New deployment
- **WHEN** a developer follows production deployment docs
- **THEN** they can configure a Feishu app and start the bot without committing secrets.

### Requirement: Transcript gate workflow
The repository MUST document or provide a helper for verifying real transcript/minutes access.

#### Scenario: Transcript unavailable
- **WHEN** the account has no readable transcript/minutes
- **THEN** the gate reports the blocker without treating it as code failure.

### Requirement: Production runbook
The repository MUST include procedures for dry-run process, approval, rejection, disabling writes, and diagnosing permission errors.

#### Scenario: Disable writes
- **WHEN** production writes need to be disabled
- **THEN** the runbook identifies the config or operational switch to enforce dry-run only.
