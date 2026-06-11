# Tiny30 Data Report

Status: Stage 1 real materialization complete and validated.

## Raw Data Detection

Current local checkout:

- MeetingBank raw data: detected under `data/raw/meetingbank`.
- QMSum raw data: detected under `data/raw/qmsum`.
- VCSum raw data: detected under `data/raw/vcsum`.

Download commands:

```bash
mkdir -p data/raw/meetingbank
curl -L -o data/raw/meetingbank/MeetingBank.zip "https://zenodo.org/records/7989108/files/MeetingBank.zip?download=1"
unzip data/raw/meetingbank/MeetingBank.zip -d data/raw/meetingbank

git clone --depth 1 https://github.com/Yale-LILY/QMSum data/raw/qmsum
git clone --depth 1 https://github.com/hahahawu/VCSum data/raw/vcsum
```

## Generated Fixture Counts

| Dataset | Generated fixtures | Manifest |
| --- | ---: | --- |
| MeetingBank | 10 | `data/manifests/meetingbank_tiny10_manifest.jsonl` |
| QMSum | 10 | `data/manifests/qmsum_tiny10_manifest.jsonl` |
| VCSum | 10 | `data/manifests/vcsum_tiny10_manifest.jsonl` |
| Total | 30 | `data/manifests/tiny30_manifest.jsonl` |

## Fixture Rows

The current `fixture_lock.json` was generated with seed `20260611`.

MeetingBank:

- 10 fixtures from `Metadata/MeetingBank.json`.
- 6 agenda-item fixtures and 4 full-meeting fixtures.
- Full-meeting fixtures resolve the referenced `Audio&Transcripts/<city>/transcripts/*.transcript.json` files and expand Azure-style segments into ordered transcript turns.

QMSum:

- 10 fixtures selected with deterministic stratification.
- Current selection includes Product, Academic, and Committee domains.
- The 10 fixtures contain 80 query-summary tasks for source-grounded QA and query-focused summarization.

VCSum:

- 10 Chinese meeting fixtures.
- Current selection includes topic segmentation cases and 2 salient-evidence fixtures with non-empty `salient_turn_ids`.

All generated fixtures validate through the canonical `MeetingFixture` Pydantic schema.

## License and Provenance

- MeetingBank fixtures carry source ids, source paths, split/domain metadata when available, and the project URL.
- QMSum fixtures carry source ids, domain, query provenance, and the GitHub source URL.
- VCSum fixtures carry source ids, Chinese meeting domain, source paths, and the GitHub source URL.

Processed fixtures include public corpus transcript text. Until license review explicitly approves committing generated fixture JSON, the committed evidence is manifests, fixture lock, scripts, tests, and reports; full processed fixture JSON remains local generated data.

## Git Boundary

Committed:

- adapter and preparation scripts,
- tests and toy raw samples,
- manifests and fixture lock when generated,
- dataset reports and governance docs.

Not committed:

- `data/raw/**`,
- `data/processed/meeting_fixtures/**/*.json`,
- private Feishu data,
- run artifacts under `runs/`,
- screenshots unless explicitly reviewed and redacted.

## Safe Metrics

Safe to use:

- public corpus development fixture count,
- schema validation rate,
- deterministic selection reproducibility,
- evidence/span metrics from public corpus eval.

Not safe to claim:

- production Feishu performance,
- customer meeting quality,
- real Lark live meeting success,
- real writeback success without a separate sandbox smoke report.

## Commands

Validation:

```bash
uv run python -m compileall nanobot/meeting_data scripts/data
uv run python -m pytest tests/meeting_data -q
uv run ruff check nanobot tests scripts
openspec validate materialize-tiny30-real-datasets
```

Materialization:

```bash
uv run python scripts/data/prepare_meetingbank.py --raw data/raw/meetingbank --out data/processed/meeting_fixtures/meetingbank/tiny10 --manifest data/manifests/meetingbank_tiny10_manifest.jsonl --limit 10 --seed 20260611
uv run python scripts/data/prepare_qmsum.py --raw data/raw/qmsum --out data/processed/meeting_fixtures/qmsum/tiny10 --manifest data/manifests/qmsum_tiny10_manifest.jsonl --limit 10 --seed 20260611
uv run python scripts/data/prepare_vcsum.py --raw data/raw/vcsum --out data/processed/meeting_fixtures/vcsum/tiny10 --manifest data/manifests/vcsum_tiny10_manifest.jsonl --limit 10 --seed 20260611
uv run python scripts/data/build_fixture_manifest.py --fixtures data/processed/meeting_fixtures --out data/manifests/tiny30_manifest.jsonl --lock data/manifests/fixture_lock.json --seed 20260611
```

## Test Results

Commands run:

```bash
uv run python -m compileall nanobot/meeting_data scripts/data
uv run python -m pytest tests/meeting_data -q
uv run ruff check nanobot tests scripts
openspec validate materialize-tiny30-real-datasets
```

Results:

- compileall: passed.
- `tests/meeting_data`: 21 passed.
- ruff: passed.
- OpenSpec: `materialize-tiny30-real-datasets` is valid.

## Known Issues

- Processed fixture JSON is intentionally treated as local generated data unless license review approves committing it.
- These are public-corpus development fixtures, not production Feishu/customer meeting metrics.
