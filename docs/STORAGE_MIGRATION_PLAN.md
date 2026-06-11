# Storage Migration Plan

Current schema version: `1`.

`SQLiteMeetingRepository` creates a `schema_meta` table and stores `schema_version` during initialization.

## Version 1

Tables:

- `runs`
- `meetings`
- `transcript_segments`
- `minutes`
- `decisions`
- `action_items`
- `risks`
- `open_questions`
- `write_operations`
- `audit_events`
- `entity_memories`
- `schema_meta`

## Migration Rules

Future migrations should:

1. run inside SQLite transactions,
2. be idempotent,
3. update `schema_meta.schema_version`,
4. preserve JSON payload compatibility or include backfill logic,
5. include restart/recovery tests.

## Current Limitation

The current repository initializes schema version 1 but does not yet include a multi-version migration runner because no historical production schema exists.
