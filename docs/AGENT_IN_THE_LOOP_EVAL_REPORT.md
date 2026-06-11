# Agent-in-the-loop Eval Report

Status: Stage 2 complete and validated.

## Fixture Source

This run used local real public-corpus tiny30 fixtures materialized from:

- MeetingBank: 10 fixtures.
- QMSum: 10 fixtures.
- VCSum: 10 fixtures.

Processed fixture JSON remains local generated data and is not committed. The committed evidence is the manifest/lock/report layer.

## Execution Profile

- Eval mode: `agent`.
- Metric scope: `public_corpus_development`.
- Real LLM: not used by default.
- Real Lark API: not used.
- Real Feishu writes: not used.
- Computer Use: not used.
- Analyzer profile: fake analyzer plus deterministic source matching unless `RUN_REAL_LLM_TESTS=1`.

## Agent Workflow Coverage

For each fixture, agent mode runs:

1. `FeishuLikeMeetingContext` construction.
2. `PreBriefWorkflow` with fake Lark provider.
3. `LiveMeetingWorkflow` transcript chunk replay.
4. `PostMeetingWorkflow` with fake analyzer.
5. Dry-run `WritePlan` generation.
6. Eval-local memory persistence.
7. Source-grounded QA artifact generation.

Artifacts are written under:

```text
runs/meeting_eval/<run_id>/<fixture_id>/artifacts/
```

Per-fixture artifacts include:

- `prebrief.md`
- `prebrief_sources.json`
- `live_state_snapshots.jsonl`
- `live_qa_answers.jsonl`
- `minutes.md`
- `decisions.json`
- `action_items.json`
- `risks.json`
- `open_questions.json`
- `write_plan.json`
- `qa_answers.jsonl`

## Tiny30 Agent Run

Command:

```bash
uv run python scripts/eval/run_meeting_eval.py --suite tiny30 --mode agent --fixtures data/processed/meeting_fixtures --out runs/meeting_eval
```

Run:

```text
tiny30-18808855-35a9-4304-99a1-455c509ab9f1
```

Summary:

- Fixtures: 30.
- Tasks: 102.
- Failures: 0.
- Workflow completion rate: 1.0.
- WritePlan dry-run rate: 1.0.
- Trace completeness: 1.0.
- Artifact consistency: 1.0.
- Memory write validity: 1.0.

Metrics:

```text
schema_valid_rate: 1.0
workflow_completion_rate: 1.0
evidence_coverage: 1.0
unsupported_claim_count: 0
span_recall: 1.0
span_precision: 0.8913043478260869
source_attribution_rate: 1.0
trace_completeness: 1.0
artifact_consistency: 1.0
streaming_stability: 1.0
memory_write_validity: 1.0
write_plan_dry_run_rate: 1.0
```

Dataset-specific metrics:

- MeetingBank agenda coverage: 1.0.
- MeetingBank segment summary similarity: 1.0.
- QMSum relevant span recall: 1.0.
- QMSum relevant span precision: 0.8611111111111112.
- QMSum insufficient evidence correctness: 0.5.
- VCSum Chinese schema stability: 1.0.
- VCSum topic boundary similarity: 1.0.
- VCSum salient evidence recall: 1.0.

## Validation

Commands run:

```bash
uv run python -m compileall nanobot/meeting_eval nanobot/meeting_data scripts/eval
uv run python -m pytest tests/meeting_eval tests/meeting_data -q
uv run ruff check nanobot tests scripts
openspec validate agent-in-the-loop-public-corpus-eval
```

Results:

- compileall: passed.
- pytest: 33 passed.
- ruff: passed.
- OpenSpec: `agent-in-the-loop-public-corpus-eval` is valid.

## What This Proves

- Public meeting fixtures can enter the actual Agent workflow path, not only mock tools.
- Agent mode can generate prebrief/live/postmeeting/QA/memory/write-plan artifacts locally.
- WritePlan operations remain dry-run and unapproved.
- Metrics are reproducible development metrics over public corpora.

## What This Does Not Prove

- It does not prove production Feishu quality.
- It does not prove real customer meeting performance.
- It does not prove real Lark live meeting listening.
- It does not prove real writeback success.
- It does not prove real LLM extraction quality unless `RUN_REAL_LLM_TESTS=1` is used and separately reported.

## Next Step

Stage 3 should use the existing `LarkToolAdapter` and sandbox targets to collect real Feishu chain evidence while keeping writes opt-in and approval-gated.
