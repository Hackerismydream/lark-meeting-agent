# V1 Release Report

Baseline commit for this report: `dd31286`.

## Product Status

Lark Meeting Agent V1.0 is a fixture-tested and fake-provider-tested Feishu/Lark meeting lifecycle agent. It covers pre-meeting briefs, visible live meeting listening flow, post-meeting minutes, approval-gated write plans, meeting memory, source-grounded QA, production bot command glue, OAPI provider boundary, SQLite run recovery, security governance, and observability.

This is not a claimed production deployment. Real Feishu channel deployment and real OpenAPI smoke remain unverified.

## Implemented Capabilities

- PreBriefWorkflow for sourced pre-meeting context.
- LiveMeetingWorkflow and LiveLarkMeetingWorkflow for visible join, event polling, live state, and live QA.
- PostMeetingWorkflow for transcript normalization, structured minutes, decisions, action items, risks, open questions, and WritePlan generation.
- Approval-gated `docs.create`, `task.create`, `im.send`, live join, and live leave operations through `LarkToolAdapter`.
- Production Feishu message mapping and command UX.
- SQLite run state recovery for status/approve/reject after restart.
- Security governance: admin config validation, separated permissions, prompt injection tests, redaction, and retention docs.
- Observability: JSON traces, audit events, operational metrics, and error taxonomy.

## Validation Summary

- Deterministic fixture metrics: see `docs/V1_BENCHMARK_REPORT.md`.
- Optional real LLM metrics: not run for this release report.
- Real Lark smoke: not run in Phase 10; no real live meeting number was provided.
- Real Feishu channel smoke: not run; requires configured Feishu app and opt-in runtime.
- Blocked/unverified: production Feishu deployment, real OAPI tenant smoke, macOS companion app, custom ASR/audio ingestion.

## Release Decision

V1.0 is ready as an engineering portfolio release and deterministic demo baseline. It is not ready to be described as deployed in production.
