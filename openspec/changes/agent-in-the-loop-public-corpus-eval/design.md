# Design: Agent-in-the-loop Public Corpus Eval

## Modes

`mock_smoke` preserves the existing runner path:

```text
fixture -> FeishuLikeMeetingContext -> MockLarkTools -> artifacts -> report
```

`agent` adds the product workflow path:

```text
fixture
  -> FeishuLikeMeetingContext
  -> PreBriefWorkflow
  -> LiveMeetingWorkflow replay
  -> PostMeetingWorkflow
  -> eval-local memory
  -> QA artifacts
  -> dry-run WritePlan assertion
  -> report / trace / predictions / failures / artifacts
```

## Storage

Each run writes under:

```text
runs/meeting_eval/<run_id>/
```

Each fixture writes under:

```text
runs/meeting_eval/<run_id>/<fixture_id>/
  artifacts/
  memory/
  transcript.txt
```

The workflow workspace for a fixture is the fixture run directory, so `.lark_meeting_agent/` memory is eval-local and cannot pollute the user's real meeting memory.

## Lark Boundary

Agent mode uses `ProviderMode.FAKE` for workflows that need a Lark adapter. It does not create CLI, OAPI, SDK, HTTP, or subprocess providers. It does not execute approval.

## LLM Boundary

Agent mode uses the fake analyzer unless `RUN_REAL_LLM_TESTS=1`. The report records whether the run used real LLM. Public corpus metrics and optional real LLM metrics remain separate.

## Metrics

The report includes `metric_scope=public_corpus_development` and records common and dataset-specific metrics. These are development metrics over public fixtures, not production Feishu/customer meeting metrics.
