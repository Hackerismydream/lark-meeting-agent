# Proposal: Production Storage and Run State

## Intent

Implement V1.0 phase `production-storage-run-state` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Repository abstraction is source of truth for production bot process/status/approve/reject.
- SQLite stores runs, write operations, audit events, meetings, segments, minutes, decisions/actions/risks/questions/entity memories.
- Approval executes inside transaction or protected critical section.
- Duplicate approve does not duplicate writes.
- External result IDs/URLs persisted.

## Scope

This change covers:

- Repository abstraction is source of truth for production bot process/status/approve/reject.
- SQLite stores runs, write operations, audit events, meetings, segments, minutes, decisions/actions/risks/questions/entity memories.
- Approval executes inside transaction or protected critical section.
- Duplicate approve does not duplicate writes.
- External result IDs/URLs persisted.
- Partial success and needs_reconciliation states supported.
- Schema version/migration metadata exists.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- Restart scenario can status/approve existing run from SQLite.
- Duplicate approve does not execute completed operation again.
- Failed write records failure and does not mark completed.
- JSONL export still works for debugging.
