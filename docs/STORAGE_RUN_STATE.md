# Storage and Run State

Production bot run state uses `SQLiteMeetingRepository` as the source of truth.

JSONL memory under `.lark_meeting_agent/` remains available for local debugging, export, source-grounded QA, and human inspection, but production `process`, `status`, `approve`, and `reject` recover from the repository.

## Stored Objects

SQLite stores:

- runs,
- meetings,
- transcript segments,
- minutes,
- decisions,
- action items,
- risks,
- open questions,
- write operations,
- audit events,
- entity memories,
- schema metadata.

Rows store typed JSON payload snapshots plus normalized keys for inspection and idempotent updates.

## Approval State

Approval is guarded by the repository's approval critical section. Completed operations are skipped on duplicate approval, so retries do not duplicate external writes.

Run status after approval:

- `completed`: all selected executable operations completed,
- `partial_success`: at least one operation completed and at least one failed,
- `needs_reconciliation`: selected writes failed and no write completed,
- `rejected`: pending writes were explicitly rejected.

Write operation results persist external IDs and URLs from the provider response.

## Debug Export

`JsonlMeetingRepository` and `MeetingMemoryStore` still write local JSONL files. This is intentionally kept for debugging and demos, but it is not the production recovery source.
