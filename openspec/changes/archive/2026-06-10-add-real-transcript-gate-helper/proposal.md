## Why

The remaining MVP gates depend on a real Feishu/Lark meeting that exposes readable transcript or minutes content to the authorized user. The current blocker is external data availability, not adapter implementation. The repository needs a repeatable read-only gate so future runs can prove whether the account has usable meeting text before attempting LLM analysis or write approval.

## What Changes

- Add a read-only transcript gate helper that searches real meetings/minutes through `LarkToolAdapter`.
- Return a structured JSON report with status, visible meeting count, readable transcript evidence, blocker reasons, and next command.
- Expose the helper through local CLI and `scripts/lma-real transcript-gate`.
- Add fake tests for both ready and blocked states.

## Impact

- No write operations.
- No real credentials required in tests.
- Does not mark the remaining real write gates complete.
