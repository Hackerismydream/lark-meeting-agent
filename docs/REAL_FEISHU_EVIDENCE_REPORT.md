# Real Feishu Evidence Report

Status: Stage 3 dry-run evidence generated and validated.

## What Uses Real Feishu

- `scripts/demo/run_feishu_prebrief_demo.py` can read real Feishu calendar agenda through `LarkToolAdapter` with `provider-mode=cli`.
- Real writes are disabled by default.
- Real writes require `LMA_DEMO_ENABLE_REAL_WRITES=1` plus `--approve`.

## What Uses Public Fixtures

- Meeting transcript content comes from public MeetingFixture data, not private Feishu minutes.
- Post-meeting minutes, decisions, action items, and QA evidence are generated from public fixtures.

## Demo Commands

Dry-run prebrief:

```bash
uv run python scripts/demo/run_feishu_prebrief_demo.py --dry-run
```

Dry-run postmeeting:

```bash
uv run python scripts/demo/run_feishu_postmeeting_demo.py --fixture-id <fixture_id> --dry-run
```

Dry-run QA:

```bash
uv run python scripts/demo/run_feishu_qa_demo.py --dry-run
```

Optional sandbox writeback:

```bash
LMA_DEMO_ENABLE_REAL_WRITES=1 uv run python scripts/demo/run_feishu_postmeeting_demo.py --fixture-id <fixture_id> --provider-mode cli --approve
```

## Evidence Paths

```text
runs/real_feishu_scenarios/scenario_01_prebrief/
runs/real_feishu_scenarios/scenario_02_postmeeting_writeback/
runs/real_feishu_scenarios/scenario_03_qa/
```

Current local dry-run evidence:

- Scenario 01 prebrief: real `calendar.agenda` read succeeded through lark-cli user identity; current returned agenda data is empty.
- Scenario 02 postmeeting writeback: public fixture `meetingbank-AlamedaCC_01022019_2019-6350`; real writes disabled; local WritePlan generated.
- Scenario 03 QA: public fixture memory seed; source-grounded QA generated; optional IM operation is `missing_target` because no sandbox chat id is configured.

## Dry-run vs Real Write

- Dry-run creates local artifacts only.
- `write_plan.json` and `optional_write_plan.json` show pending/missing-target operations.
- Real writes are only attempted when env and approval flags are both present.

## Redaction

Evidence output is sanitized for token, secret, cookie, authorization, chat id, open id, user id, email, and phone-like keys.

## Screenshot Status

Screenshots are not captured automatically in Stage 3. See `docs/REAL_FEISHU_SCREENSHOT_CHECKLIST.md`.

## Validation

Commands run:

```bash
uv run python -m compileall scripts/demo nanobot/meeting_data nanobot/meeting_eval
uv run python -m pytest tests/demo tests/meeting_data tests/meeting_eval -q
uv run ruff check nanobot tests scripts
openspec validate real-feishu-sandbox-evidence
LARK_CLI_NO_PROXY=1 uv run python scripts/demo/run_feishu_prebrief_demo.py --dry-run
uv run python scripts/demo/run_feishu_postmeeting_demo.py --fixture-id meetingbank-AlamedaCC_01022019_2019-6350 --dry-run
uv run python scripts/demo/run_feishu_qa_demo.py --dry-run
```

Results:

- compileall: passed.
- pytest: 39 passed.
- ruff: passed.
- OpenSpec: valid.
- real Feishu calendar dry-run: succeeded, no agenda items returned for current range.
- postmeeting dry-run: succeeded.
- QA dry-run: succeeded.

## Cannot Claim

- No live meeting listening success.
- No private customer meeting performance.
- No production Feishu writeback quality.
- No real LLM extraction quality unless separately run with opt-in LLM settings.
