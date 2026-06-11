# Demo Evidence Report

Demo date: 2026-06-11

Git commit at screenshot time: `747fd95`

Stage 4 commit: see git history for this report commit.

## Summary

This is a product demo evidence pass, not a benchmark and not CI. It uses Stage 2/3 artifacts to show the Lark Meeting Agent user path with screenshots. Real Feishu writeback was not executed in this pass.

## Data Sources

- Public dataset fixtures: MeetingBank/QMSum/VCSum tiny30 manifests and local generated fixture JSON.
- Real Feishu: calendar agenda read through lark-cli user identity in Stage 3; current agenda result was empty.
- Local artifacts: prebrief, minutes, action items, write plans, QA answers, trace files, and eval reports.
- Dry-run evidence: postmeeting WritePlan and optional QA IM message.

## Screenshot List

Captured screenshots:

1. `runs/demo_evidence/screenshots/02_prebrief_doc.png`
   - Source: `runs/real_feishu_scenarios/scenario_01_prebrief/prebrief.md`
   - Status: passed, local artifact screenshot.

2. `runs/demo_evidence/screenshots/03_minutes_doc.png`
   - Source: `runs/real_feishu_scenarios/scenario_02_postmeeting_writeback/minutes.md`
   - Status: passed, public fixture / dry-run artifact screenshot.

3. `runs/demo_evidence/screenshots/04_tasks.png`
   - Source: `runs/real_feishu_scenarios/scenario_02_postmeeting_writeback/action_items.json`
   - Status: passed, local task extraction artifact screenshot.

4. `runs/demo_evidence/screenshots/05_sandbox_message.png`
   - Source: `runs/real_feishu_scenarios/scenario_03_qa/optional_write_plan.json`
   - Status: dry-run only; no sandbox chat id configured.

5. `runs/demo_evidence/screenshots/06_eval_report.png`
   - Source: `docs/AGENT_IN_THE_LOOP_EVAL_REPORT.md`
   - Status: passed, public-corpus development metric screenshot.

6. `runs/demo_evidence/screenshots/07_trace_audit.png`
   - Source: `runs/real_feishu_scenarios/scenario_02_postmeeting_writeback/trace.jsonl`
   - Status: passed, local trace screenshot.

Blocked screenshot:

- `01_calendar_agenda.png`: blocked because the real Feishu calendar agenda read succeeded but returned no demo meeting for the current range. See `runs/demo_evidence/blockers.md`.

## Commands

```bash
LARK_CLI_NO_PROXY=1 uv run python scripts/demo/run_feishu_prebrief_demo.py --dry-run
uv run python scripts/demo/run_feishu_postmeeting_demo.py --fixture-id meetingbank-AlamedaCC_01022019_2019-6350 --dry-run
uv run python scripts/demo/run_feishu_qa_demo.py --dry-run
```

Screenshot source pages were generated under:

```text
runs/demo_evidence/pages/
```

Screenshots were captured from local Chrome-rendered artifact pages under:

```text
runs/demo_evidence/screenshots/
```

Computer Use was used to inspect the local PreBrief demo page in Chrome before screenshot capture.

## Scenario Status

| Scenario | Status | Evidence type |
| --- | --- | --- |
| Feishu calendar agenda | blocked for screenshot | real Feishu read, empty agenda |
| Prebrief | passed | local artifact from real calendar read + public fixture context |
| Meeting minutes | passed | public fixture + local dry-run artifact |
| Tasks | dry-run only | local action item / WritePlan artifact |
| Sandbox message | dry-run only | local optional IM WritePlan artifact |
| Eval report | passed | public-corpus development report |
| Trace / audit | passed | local trace artifact |

## Privacy

- No access tokens, cookies, app secrets, private chats, or private customer names are shown.
- Screenshots are based on local artifacts and public fixture text.
- Real Feishu UI screenshot was skipped because there was no safe visible demo meeting to capture.

## Cannot Claim

- These screenshots do not prove production Feishu usage.
- They do not prove live meeting listening.
- They do not prove real writeback because Stage 3 ran dry-run.
- Public corpus metrics are development metrics, not customer/production metrics.

## Follow-up Blockers

- Create or identify a sandbox calendar event to capture `01_calendar_agenda.png`.
- Configure `LMA_DEMO_CHAT_ID` and explicitly approve sandbox writes if real docs/tasks/IM screenshots are needed.
- Run a separate live meeting smoke before claiming live meeting listening.
