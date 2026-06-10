# Testing Strategy

Lark Meeting Agent V1 uses text/event-first testing as the primary development path.

The default test suite must not require real Lark credentials, real LLM keys, real meetings, or paid Feishu minutes. Real Lark and real LLM tests are opt-in smoke tests.

## Test Layers

1. Schema and invariant tests: Pydantic models, evidence refs, approval state, write status.
2. Pure workflow tests: normalizer, fake analyzer, prebrief, live state, post-meeting process, memory, QA.
3. Lark adapter contract tests: allowlist, read/write split, dry-run, approval, audit, redaction.
4. Live event conversion tests: transcript, chat, participant, share, unknown, malformed, duplicate events.
5. Live simulator replay: scenario fixtures become Lark-like event pages with `has_more` and `page_token`.
6. Lifecycle replay: prebrief, live replay, post-meeting dry-run write plan, source-grounded QA.
7. Opt-in real smoke: `lark-cli` auth, visible live join, event poll, live QA, visible leave.
8. Optional later evals: real LLM benchmark, RAG faithfulness, red-team, observability, audio/ASR robustness.

## Default Pass Criteria

- `uv run python -m pytest tests/meeting -q` passes without credentials.
- Simulator scenarios replay deterministically.
- Decision/action candidates retain evidence.
- QA sources cite expected segment ids.
- Prompt injection content remains data and cannot approve writes.
- Real smoke tests skip unless explicitly requested.

## Non-Goals

- No custom ASR in V1.0.
- No production claims from fixture metrics.
- No required Ragas, DeepEval, Promptfoo, Phoenix, Temporal, Celery, or Dramatiq.
