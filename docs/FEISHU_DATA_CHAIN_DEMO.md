# Feishu Data Chain Demo

The demo separates content data from product-chain evidence.

Content ability:

```text
MeetingBank / QMSum / VCSum
-> MeetingFixture
-> FeishuLikeMeetingContext
-> transcript stream, agenda doc, participants, output targets
```

Product chain:

```text
FeishuLikeMeetingContext
-> prebrief / live simulation / postmeeting / QA
-> WritePlan
-> approval
-> mock local artifacts or opt-in sandbox Feishu writes
```

## Commands

Prebrief:

```bash
uv run python scripts/demo/run_feishu_prebrief_demo.py --query "项目例会"
```

Postmeeting dry-run:

```bash
uv run python scripts/demo/run_feishu_postmeeting_demo.py \
  --fixture data/processed/meeting_fixtures/qmsum/tiny10/<fixture>.json
```

QA:

```bash
uv run python scripts/demo/run_feishu_qa_demo.py \
  --fixtures data/processed/meeting_fixtures
```

## Real Write Guard

Real writes require all of:

- `LMA_DEMO_ENABLE_REAL_WRITES=1`
- sandbox chat/doc/task target
- existing backend approval path
- Lark operations through `LarkToolAdapter`

Default mode is dry-run.
