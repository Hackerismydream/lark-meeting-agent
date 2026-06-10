# Fixture Guide

Scenario fixtures live under:

```text
tests/fixtures/meeting/scenarios/<scenario_id>/
```

Each scenario contains:

- `scenario.json`: metadata, participants, agenda, project/customer labels.
- `agenda.md`: human-readable agenda.
- `memory_seed.json`: history and open actions used by replay docs and future seeders.
- `timeline.jsonl`: simulated meeting event stream.
- `expected.json`: expected decisions, actions, QA sources, and safety cases.
- `qa_cases.json`: duplicated QA cases for review convenience.
- `safety_cases.json`: prompt-injection and approval-bypass cases.

## Required Scenario Coverage

Every scenario must include:

- one transcript event,
- one chat event,
- one participant event,
- one decision or decision candidate,
- one action item or action candidate,
- one source-grounded QA case,
- one prompt injection or tool safety risk.

## Event Fields

`timeline.jsonl` rows use these fields:

- `event_id`
- `event_type`
- `ts_ms`
- `speaker_id`
- `speaker_name`
- `text`
- `segment_id`
- `tags`
- `payload`

The simulator converts these rows into Lark-like raw event pages.
