# Design: Materialize Tiny30 Real Datasets

## Flow

```text
raw public dataset
-> dataset adapter
-> Canonical MeetingFixture
-> processed fixture JSON
-> manifest
-> fixture lock
-> data report
```

## Determinism

All selectors accept `seed=20260611` by default. Preparation scripts expose `--limit` and `--seed` so the generated tiny30 can be reproduced.

## Adapter Hardening

MeetingBank supports root-level JSON files, split files, metadata files, and transcript folders where available. QMSum supports `data/ALL`, `data/Academic`, `data/Product`, and `data/Committee`. VCSum supports root files and `vcsum_data`.

Adapters prefer records with:

- non-empty transcript,
- reference summary or query answer,
- usable split/domain metadata,
- richer agenda/topic/evidence fields.

## Governance

Raw datasets are ignored by git. Processed fixtures may include large public transcript excerpts, so reports and manifests are the primary committed evidence; generated fixture JSON can be local unless license review explicitly approves committing a sample pack.

## Failure Mode

If raw data is missing, scripts exit with clear download commands instead of obscure stack traces.
