# Proposal: Agent-in-the-loop Public Corpus Eval

## Summary

Add an `agent` evaluation mode that routes public meeting fixtures through the real Lark Meeting Agent workflows: pre-brief generation, live transcript replay, post-meeting processing, source-grounded QA, dry-run WritePlan generation, and eval-local memory persistence.

## Motivation

The tiny30 public corpus is useful only if it exercises the same workflow boundaries as the product. The current mock smoke runner verifies fixture loading and local artifact creation, but it does not prove the Agent workflows can consume public corpus meetings end to end.

## Scope

- Keep `mode=mock_smoke` for fast local smoke tests.
- Add `mode=agent`.
- Run fixtures through `PreBriefWorkflow`, `LiveMeetingWorkflow`, `PostMeetingWorkflow`, meeting memory, QA artifact generation, and dry-run WritePlan validation.
- Generate report, trace, predictions, failures, and per-fixture artifacts.
- Keep metrics explicitly scoped to `public_corpus_development`.

## Non-goals

- No real Lark API calls.
- No real Feishu writes.
- No Computer Use.
- No production metric claims.
- No mandatory real LLM calls. Real LLM remains opt-in through `RUN_REAL_LLM_TESTS=1`.

## Validation

```bash
uv run python -m compileall nanobot/meeting_eval nanobot/meeting_data scripts/eval
uv run python -m pytest tests/meeting_eval tests/meeting_data -q
uv run ruff check nanobot tests scripts
openspec validate agent-in-the-loop-public-corpus-eval
```

When tiny30 exists:

```bash
uv run python scripts/eval/run_meeting_eval.py --suite tiny30 --mode agent --fixtures data/processed/meeting_fixtures --out runs/meeting_eval
```
