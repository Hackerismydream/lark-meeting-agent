# Lifecycle Delivery Report

## Delivered

- Added `PreBriefWorkflow` for sourced meeting preparation from agenda, docs/tasks, historical memory, and entity memory.
- Added `LiveMeetingWorkflow` for incremental transcript/event ingestion, rolling live state, decision/action/risk/question candidates, and source-grounded live QA.
- Preserved and extended `PostMeetingWorkflow` for structured minutes, evidence-linked decisions/action items, write plans, approval, and memory persistence.
- Added `MemoryWorkflow`, layered JSONL records, entity memories, open action lookup, retrieval metadata, and trace links.
- Added local retrieval with structured filters and keyword scoring plus an optional deterministic semantic retriever interface.
- Extended `LarkToolAdapter` lifecycle reads for calendar agenda, task lookup, doc search/fetch, VC notes/search, and minutes search.
- Kept writes limited to `docs.create`, `task.create`, and `im.send`, with dry-run and explicit approval.
- Added run trace persistence with secret/private URL redaction.
- Extended `lark_meeting` tool actions to `prebrief`, `live_ingest`, `live_qa`, `process`, `approve`, `qa`, `status`, and `evaluate`.
- Added 31 lifecycle benchmark cases and metric reporting.

## Local Validation

```bash
uv run python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py
uv run python -m pytest tests/meeting -q
uv run ruff check nanobot tests
openspec validate deliver-lifecycle-meeting-agent
```

Latest local result:

```text
compileall passed
41 passed, 3 skipped
ruff passed
OpenSpec change valid
scripts/lma-real status passed
```

## Benchmark Evidence

Command:

```bash
uv run python -m nanobot.meeting.cli evaluate \
  --cases tests/fixtures/meeting/evaluation/lifecycle_cases.json \
  --output /tmp/lma-lifecycle-smoke/eval.json
```

Result on the bundled 31-case deterministic fixture regression benchmark:

```text
profile: deterministic-regression
action_precision: 1.0
action_recall: 1.0
decision_precision: 1.0
decision_recall: 1.0
evidence_coverage: 1.0
schema_validation_success_rate: 1.0
tool_call_success_rate: 1.0
qa_source_accuracy: 1.0
safety_pass_rate: 1.0
passed: true
```

These are deterministic fixture-benchmark metrics, not production deployment metrics and not real LLM extraction metrics.

Optional real LLM extraction benchmark fixtures are available at `tests/fixtures/meeting/evaluation/llm_extraction_cases.json`. They are skipped by default and run only with:

```bash
RUN_REAL_LLM_TESTS=1 uv run python -m pytest tests/meeting -q
```

Do not claim LLM extraction benchmark metrics unless that opt-in command has actually been run.

## Real Lark Status

Real Lark integration remains routed through `scripts/lma-real` and `lark-cli`.

Supported helper commands:

```bash
scripts/lma-real status
scripts/lma-real prebrief --query "项目例会" --meeting-type project_sync --project Alpha
scripts/lma-real live-join --meeting-number <9-digit-meeting-number> --approve-visible-join
scripts/lma-real live-poll --meeting-id <returned-long-meeting-id> --live-run-id <returned-live-run-id>
scripts/lma-real live-leave --meeting-id <returned-long-meeting-id> --approve-visible-leave
scripts/lma-real process --latest-ended --query "项目例会" --create-doc --create-tasks --dry-run
scripts/lma-real approve --run-id <run_id> --operation-ids <op1,op2>
```

The primary real path is now live meeting listening and requires a currently running 9-digit meeting number. The current account can authenticate and search visible VC meetings, but readable historical minutes/transcript content remains account-data dependent. That historical limitation is documented in `docs/BLOCKERS.md`.

Operation-level real-smoke status is tracked in `docs/LARK_CLI_VERIFICATION_MATRIX.md`.

## Not Claimed

- No custom ASR.
- No invisible or automatic meeting capture.
- No unapproved realtime VC control.
- No production OAuth onboarding.
- No mandatory PostgreSQL/vector database service.
- No autonomous free-form Lark tool calling.
