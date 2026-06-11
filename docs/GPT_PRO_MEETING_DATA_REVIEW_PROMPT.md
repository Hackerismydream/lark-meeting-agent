Please review this repository as a senior agent-product engineer and meeting-workflow systems reviewer.

Repository: https://github.com/Hackerismydream/lark-meeting-agent
Branch: main

Context:

Lark Meeting Agent is a Feishu/Lark-native meeting workflow agent built inside a HKUDS/nanobot-based codebase. The current question is not whether the whole product is production-ready. The question is whether the new meeting-data bootstrap strategy is a reasonable way to keep development moving when there are no real customer users and real in-meeting data is blocked by external Feishu/Lark permissions.

Please review these files first:

- `docs/MEETING_DATA_BOOTSTRAP_STRATEGY.md`
- `docs/LIVE_LARK_SMOKE_RESULTS.md`
- `docs/LIVE_LARK_SMOKE_RUNBOOK.md`
- `docs/REAL_LIVE_GATE.md`
- `docs/TESTING_STRATEGY.md`
- `docs/BLOCKERS.md`
- `nanobot/meeting/live_lark.py`
- `nanobot/meeting/lark_adapter.py`
- `tests/meeting/test_real_smoke_scripts.py`
- `tests/meeting/test_live_simulator.py`

The current proposed strategy has three layers:

1. Use open meeting corpora for breadth and reproducibility:
   - MeetingBank for long meeting summarization, agenda/minutes alignment, and item summaries.
   - QMSum for source-grounded QA and query-specific summarization.
   - AMI and ICSI for multi-party transcript normalization, speaker turns, and live replay stress cases.
2. Use LLM-generated Feishu-style business fixtures for product-specific scenarios that public corpora do not cover:
   - project weekly meetings,
   - requirement reviews,
   - incident reviews,
   - customer PoC reviews,
   - sales/CS follow-ups,
   - one-on-one meetings,
   - approval/writeback edge cases,
   - prompt-injection and unsafe write requests.
3. Use opt-in real live smoke as the primary real integration gate:
   - visible bot join,
   - event polling,
   - live QA with sources or insufficient-evidence response,
   - visible leave,
   - no committed private transcript content.

Current real smoke evidence:

```bash
scripts/lma-real live-smoke \
  --meeting-number 414936709 \
  --approve-visible-join \
  --approve-visible-leave \
  --export-raw-event-shapes /tmp/lma-live-event-shapes-414936709.json
```

Observed result:

- First attempt failed because the Feishu user token lacked `vc:meeting.bot.join:write`.
- That scope was then granted successfully.
- Second attempt still failed before join with `HTTP 403: no permission`.
- No join/poll/leave happened.
- No raw event shapes were exported.
- Current classification is `blocked / permission / event_count=0`.

Local verification reported:

```bash
uv run python -m pytest tests/meeting/test_real_smoke_scripts.py tests/meeting/test_live_simulator.py -q
```

Result:

```text
8 passed, 1 skipped
```

Please answer these review questions:

1. Is the three-layer strategy technically reasonable, or does it create a misleading product/evaluation story?
2. Are MeetingBank, QMSum, AMI, and ICSI appropriate open corpora for this product, and what are their main gaps?
3. Is it acceptable to use LLM-generated Feishu-style fixtures for CI/regression if they are explicitly not claimed as production metrics?
4. Does the current real smoke result support the conclusion that the remaining blocker is external Feishu/Lark permission or tenant/meeting configuration, not local workflow code?
5. Are the documented pass/block conditions strict enough to prevent inflated claims?
6. What additional fixture types or negative cases should be added before this project is described as a credible engineering demo?
7. Are there any safety risks in the plan, especially around synthetic data, prompt injection, approval bypass, private transcript leakage, or overclaiming real integration?

Review format:

- Findings first, ordered by severity.
- Cite exact file paths and line numbers wherever possible.
- For each issue, explain the failure mode and the smallest concrete fix.
- Keep product advice scoped to the meeting-data strategy and live-smoke validation path.
- Do not suggest production OAuth, a frontend dashboard, custom ASR, vector databases, or deployment work unless it is necessary to fix a concrete flaw in this strategy.

End with:

1. Whether the strategy is reasonable as the next step.
2. The top three changes needed before relying on it in a public demo or interview.
3. The most important missing test or fixture.
4. Whether the current wording avoids overclaiming real Lark integration.
