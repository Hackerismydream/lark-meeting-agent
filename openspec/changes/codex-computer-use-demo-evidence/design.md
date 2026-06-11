# Design: Codex Computer Use Demo Evidence

## Approach

The demo pass uses the Stage 3 evidence pack as source material. Local artifacts are rendered for screenshots when real Feishu writes are unavailable or intentionally disabled.

## Screenshot Sources

- Real Feishu calendar: blocker if no safe demo meeting is visible.
- Prebrief: local `scenario_01_prebrief/prebrief.md`.
- Minutes: local `scenario_02_postmeeting_writeback/minutes.md`.
- Tasks: local `scenario_02_postmeeting_writeback/action_items.json` or `write_plan.json`.
- Message: local `scenario_03_qa/optional_write_plan.json`.
- Eval report: local `docs/AGENT_IN_THE_LOOP_EVAL_REPORT.md` or run report.
- Trace/audit: local scenario trace files.

## Privacy

Screenshots must use sandbox data or local public-fixture artifacts. If a UI view contains sensitive unrelated data, the step is skipped and recorded as blocked.
