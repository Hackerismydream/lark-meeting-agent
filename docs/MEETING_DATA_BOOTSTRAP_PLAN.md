# Meeting Data Bootstrap Plan

## Purpose

We need reproducible real-human meeting data before we have real customer meetings. Public datasets are used for content ability and deterministic development. They are not production Feishu metrics.

## Datasets

MeetingBank:

```bash
mkdir -p data/raw/meetingbank
curl -L -o data/raw/meetingbank/MeetingBank.zip "https://zenodo.org/records/7989108/files/MeetingBank.zip?download=1"
unzip data/raw/meetingbank/MeetingBank.zip -d data/raw/meetingbank
```

QMSum:

```bash
git clone --depth 1 https://github.com/Yale-LILY/QMSum data/raw/qmsum
```

VCSum:

```bash
git clone --depth 1 https://github.com/hahahawu/VCSum data/raw/vcsum
```

## Prepare Tiny Fixtures

```bash
uv run python scripts/data/prepare_meetingbank.py
uv run python scripts/data/prepare_qmsum.py
uv run python scripts/data/prepare_vcsum.py
uv run python scripts/data/build_fixture_manifest.py
```

Scripts fail with these commands if raw data is missing.

## Evaluation

```bash
uv run python scripts/eval/run_meeting_eval.py \
  --suite tiny30 \
  --fixtures data/processed/meeting_fixtures \
  --out runs/meeting_eval
```

## Feishu Chain Demo

The public fixture path is:

```text
MeetingFixture -> FeishuLikeMeetingContext -> mock/real-safe workflows -> local evidence
```

Real Feishu writes are disabled by default. To enable sandbox-only writes:

```bash
export LMA_DEMO_ENABLE_REAL_WRITES=1
export LMA_DEMO_SANDBOX_CHAT_ID=<sandbox chat id>
```

Do not use arbitrary production chat/doc/task targets.
