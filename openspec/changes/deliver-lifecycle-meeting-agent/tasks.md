## 1. OpenSpec Planning

- [x] 1.1 Create `deliver-lifecycle-meeting-agent` proposal, design, task list, and delta specs.
- [x] 1.2 Validate `openspec validate deliver-lifecycle-meeting-agent`.
- [x] 1.3 Commit planning artifacts as the first reviewable unit.

## 2. Schema and Trace Foundation

- [x] 2.1 Add Pydantic schemas for pre-brief requests/results, live meeting events/state/answers, retrieval results, entity memories, evaluation cases/reports, and run traces.
- [x] 2.2 Add schema tests for required sources, evidence validation, incomplete candidates, and backward compatibility with current post-meeting snapshots.
- [x] 2.3 Add run trace writer with redaction and tests for token/private URL redaction.

## 3. LarkToolAdapter Lifecycle Reads

- [x] 3.1 Extend adapter allowlist with lifecycle read operations for `calendar.agenda`, task lookup, document search/fetch, meeting metadata, and existing VC/minutes reads.
- [x] 3.2 Implement fake provider fixtures for agenda, task lookup, document search/fetch, and meeting metadata.
- [x] 3.3 Extend CLI provider argv construction for supported read operations, keeping `shell=False`, JSON parsing, timeout, and bounded retry behavior.
- [x] 3.4 Add adapter tests for allowlist rejection, retry/audit behavior, malformed output, and write approval boundaries.

## 4. Memory and Retrieval

- [x] 4.1 Extend `MeetingMemoryStore` with layered records for entity memories, open action item index, retrieval metadata, and trace links.
- [x] 4.2 Keep existing MVP JSONL and run snapshot reads backward compatible.
- [x] 4.3 Implement retrieval engine with structured filters and keyword scoring.
- [x] 4.4 Add optional semantic retrieval interface with deterministic local test implementation and fallback when no vector backend is configured.
- [x] 4.5 Add memory/retrieval tests for project, customer, person, time range, open action item, insufficient evidence, and old snapshot loading.

## 5. PreBriefWorkflow

- [x] 5.1 Implement `PreBriefWorkflow` using adapter reads, memory retrieval, open action item lookup, related docs, and entity memories.
- [x] 5.2 Add meeting-type templates for customer meeting, project sync, requirement review, technical review, incident review, and one-on-one.
- [x] 5.3 Ensure pre-brief workflow is read-only and persists a run trace.
- [x] 5.4 Add fixtures and tests for pre-brief output sections, source references, and no-write behavior.

## 6. LiveMeetingWorkflow

- [x] 6.1 Implement incremental transcript/event ingestion with live run state.
- [x] 6.2 Maintain rolling summary, current topic, decision candidates, action item candidates, risks, disagreements, and open questions.
- [x] 6.3 Implement live QA with meeting_id, segment_id, speaker, timestamp, and insufficient-evidence behavior.
- [x] 6.4 Add fixture event-stream replay tests and prompt-injection safety tests.

## 7. PostMeetingWorkflow and WritePlan Extensions

- [x] 7.1 Preserve existing post-meeting process/approve/status/QA behavior.
- [x] 7.2 Route completed meeting outputs through `MemoryWorkflow` to update layered memories and retrieval indexes.
- [x] 7.3 Ensure write plans continue to support docs, tasks, optional IM, partial approval, missing target skip, and persisted audit results.
- [x] 7.4 Add regression tests using the existing sample transcript fixture.

## 8. Lifecycle Entrypoint

- [x] 8.1 Extend `lark_meeting` tool schema/actions with `prebrief`, `live_ingest`, `live_qa`, and `evaluate` while preserving existing actions.
- [x] 8.2 Update `nanobot/skills/lark-meeting/SKILL.md` with lifecycle instructions and Lark boundary constraints.
- [x] 8.3 Add tool route tests for every lifecycle action and error path.

## 9. Evaluation and Metrics

- [x] 9.1 Add 30+ compact synthetic/sanitized meeting fixtures with expected decisions, action items, evidence refs, QA answers, and safety cases.
- [x] 9.2 Implement evaluation runner for normalization, extraction, evidence, write-plan safety, tool-call safety, and QA citation accuracy.
- [x] 9.3 Emit JSON benchmark report with aggregate metrics, case-level failures, and trace paths.
- [x] 9.4 Add acceptance profile requiring action precision >= 90%, action recall >= 85%, evidence coverage = 100%, and safety regression pass rate = 100%.
- [x] 9.5 Add tests for metric calculations and failing-threshold behavior.

## 10. Real Smoke and Documentation

- [ ] 10.1 Extend `scripts/lma-real` or add lifecycle smoke commands for status, prebrief, process, QA, and evaluation.
- [ ] 10.2 Keep real DeepSeek and lark-cli credentials out of repository files, tests, fixtures, logs, and docs.
- [ ] 10.3 Update README, project brief, blockers, delivery report, and resume evidence notes to reflect lifecycle implementation status.
- [ ] 10.4 Document account-dependent real Lark minutes limitations separately from code-path validation.

## 11. Validation and Commits

- [x] 11.1 Run `python -m compileall nanobot/meeting nanobot/agent/tools/lark_meeting.py`.
- [x] 11.2 Run `pytest tests/meeting -q`.
- [x] 11.3 Run `ruff check nanobot tests`.
- [x] 11.4 Run `openspec validate deliver-lifecycle-meeting-agent`.
- [x] 11.5 Run fake lifecycle CLI/tool smoke tests.
- [ ] 11.6 Run optional real smoke where local Lark/DeepSeek access allows and document blockers.
- [ ] 11.7 Commit implementation in reviewable slices matching the task groups.
