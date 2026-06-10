# Storage Spec

## Purpose

Define meeting-agent state persistence contracts for local development and production MVP operation.

## Requirements

### Requirement: Repository abstraction
Production bot state MUST be stored through repository interfaces for runs, write operations, audit events, meetings, and memory records.

#### Scenario: Run persisted
- **WHEN** a process command creates a run
- **THEN** the run, write operations, and audit events are persisted through repositories.

### Requirement: SQLite production MVP backend
The production MVP MUST support SQLite storage for runs, meetings, transcript segments, minutes, decisions, action items, risks, open questions, write operations, audit events, and entity memories.

#### Scenario: SQLite approval transaction
- **WHEN** selected operations are approved
- **THEN** approval state and operation execution state are updated transactionally.

### Requirement: JSONL local backend retained
The existing JSONL local/dev backend MUST remain supported.

#### Scenario: Local fixture tests
- **WHEN** tests run without database configuration
- **THEN** JSONL-backed local behavior still works.
