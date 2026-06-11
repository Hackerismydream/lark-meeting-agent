# Design: Meeting Data Bootstrap and Feishu Chain Tiny30

## Data Model

`nanobot/meeting_data/schemas.py` defines `MeetingFixture` as the canonical interchange model. It captures metadata, agenda, transcript turns, chunks, topic segments, query tasks, optional expected artifacts, provenance, and Feishu-like context targets.

The schema validates local integrity:

- fixture id is required,
- dataset is one of `meetingbank`, `qmsum`, or `vcsum`,
- provenance is required,
- transcript turns are non-empty,
- turn, agenda, and query ids are unique within the fixture,
- query `relevant_turn_ids` point to existing transcript turns.

## Dataset Adapters

Adapters convert raw dataset formats into `MeetingFixture` without requiring raw data in tests. Scripts fail early with download instructions when full raw data is missing. Toy samples under tests exercise the parsing paths.

- MeetingBank: long meeting and agenda/minutes alignment.
- QMSum: source-grounded query-focused QA and summarization.
- VCSum: Chinese meeting summarization, topic segmentation, and salient evidence.

## Feishu Chain Bridge

`FeishuLikeMeetingContext` lets public fixtures run as if they came from Feishu calendar, agenda docs, participants, transcript stream, chat events, related docs, output targets, and approval policy.

Mock Lark tools write local artifacts only. Real demo scripts use dry-run by default and require `LMA_DEMO_ENABLE_REAL_WRITES=1` plus sandbox targets for any real write.

## Evaluation

The tiny30 suite loads generated fixtures, builds Feishu-like contexts, streams transcripts, runs local mock workflows, writes trace/artifacts, and computes deterministic metrics. Optional semantic metrics can be added later but are not required gates.

Metrics are separated into:

- public corpus metrics,
- synthetic/mock workflow metrics,
- real Feishu demo evidence,
- real Lark live smoke status.

## Risk Controls

- No raw datasets in git.
- No real Feishu calls in tests or CI.
- No audio processing.
- Public dataset metrics are not production claims.
- Meeting content is treated as untrusted input.
