# OSS Tooling Decisions

## Adopt Now

- Hypothesis: property-based fuzz tests for raw event conversion. It is a dev/test dependency and tests skip cleanly if the dev extra is not installed.
- Freezegun: deterministic time tests for live session timestamps, freshness, due dates, and trace timestamps. It is a dev/test dependency and tests skip cleanly if the dev extra is not installed.
- lark-cli: real local smoke provider only, never required by default tests.

## Defer or Keep Optional

- Syrupy: useful for snapshot tests, deferred until output surfaces stabilize.
- Ragas: optional QA/RAG evaluator, not a default dependency.
- DeepEval: optional real LLM benchmark, gated by real LLM env vars.
- Promptfoo: optional red-team suite, not part of Python runtime.
- OpenTelemetry/Phoenix: optional observability export, JSONL traces stay source of truth.
- faster-whisper/pyannote/Silero: optional audio/ASR robustness, not V1.0 core.

## Not Adopted

- Temporal, Celery, Dramatiq: too heavy for current deterministic workflow and local replay needs.
