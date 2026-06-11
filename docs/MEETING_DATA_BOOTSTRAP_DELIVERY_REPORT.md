# Meeting Data Bootstrap Delivery Report

Status: implemented.

## Files Added

- OpenSpec change: `openspec/changes/meeting-data-and-feishu-chain-tiny30/`
- Schemas and fixture utilities: `nanobot/meeting_data/`
- Evaluation runner: `nanobot/meeting_eval/`
- Data scripts: `scripts/data/`
- Eval script: `scripts/eval/run_meeting_eval.py`
- Demo scripts: `scripts/demo/`
- Tests: `tests/meeting_data/`, `tests/meeting_eval/`
- Docs: dataset plan, cards, Feishu chain demo, eval tasks, screenshot checklist.

## Datasets Supported

- MeetingBank tiny10 adapter for long meeting and agenda/minutes alignment.
- QMSum tiny10 adapter for source-grounded QA/query summarization.
- VCSum tiny10 adapter for Chinese summary/topic/salient evidence.

## Download Commands

See `docs/MEETING_DATA_BOOTSTRAP_PLAN.md` and `data/raw/README.md`.

## Tiny10 Selection Rule

Selection is deterministic with seed `20260611`. Scripts prefer non-empty transcripts and usable summaries/queries/topics where available, then write `data/manifests/<dataset>_tiny10_manifest.jsonl`.

## Generated Artifacts

The eval runner writes:

- `report.json`
- `trace.jsonl`
- `predictions.jsonl`
- `failures.jsonl`
- per-fixture local artifacts under `artifacts/`

## Requires Local Raw Data

Full MeetingBank, QMSum, and VCSum preparation requires local raw data under `data/raw/`. Tests use toy raw samples and do not require full raw datasets.

## Commands Run

```bash
uv run python -m compileall nanobot/meeting_data nanobot/meeting_eval
uv run python -m pytest tests/meeting_data tests/meeting_eval -q
uv run ruff check nanobot tests scripts
openspec validate meeting-data-and-feishu-chain-tiny30
```

Results:

- compileall: passed
- pytest: 26 passed
- ruff: passed
- OpenSpec: valid

Toy CLI smoke:

```bash
uv run python scripts/data/prepare_meetingbank.py --raw tests/fixtures/meeting_data/raw_samples/meetingbank --out /tmp/lma_tiny30_fixtures/meetingbank/tiny10 --manifest /tmp/lma_tiny30_manifests/meetingbank.jsonl
uv run python scripts/data/prepare_qmsum.py --raw tests/fixtures/meeting_data/raw_samples/qmsum --out /tmp/lma_tiny30_fixtures/qmsum/tiny10 --manifest /tmp/lma_tiny30_manifests/qmsum.jsonl
uv run python scripts/data/prepare_vcsum.py --raw tests/fixtures/meeting_data/raw_samples/vcsum --out /tmp/lma_tiny30_fixtures/vcsum/tiny10 --manifest /tmp/lma_tiny30_manifests/vcsum.jsonl
uv run python scripts/eval/run_meeting_eval.py --suite tiny30 --fixtures /tmp/lma_tiny30_fixtures --out /tmp/lma_tiny30_runs
```

Result: 3 toy fixtures, 5 tasks, no failures, report/trace/predictions/failures generated.

## Safe to Claim

- Public corpus fixture schema and adapters exist.
- Toy adapter tests run without raw public datasets.
- Mock Feishu-like chain writes local artifacts and traces.
- Eval runner computes deterministic development metrics.
- Real Feishu demo scripts default to dry-run and require opt-in writes.

## Must Not Claim

- Public dataset metrics are production Feishu metrics.
- Raw customer data was used.
- Audio or ASR was implemented.
- Real Feishu writes were executed unless a separate sandbox smoke report proves it.
- Real Lark live meeting smoke succeeded unless separately verified.

## How Public Datasets and Feishu Chain Work Together

Public datasets provide real-human meeting content. `FeishuLikeMeetingContext` wraps that content into calendar, agenda, participant, transcript stream, chat, related-doc, target, and approval-policy objects so current meeting workflows and mock Lark tools can be exercised without private data. Real Feishu evidence is collected separately through dry-run-first sandbox scripts.
