# Observability

The production MVP uses local structured traces and audit events as the observability source of truth.

## Run Traces

`RunTraceWriter` writes JSON traces under:

```text
.lark_meeting_agent/traces/<run_id>.json
```

Post-meeting processing emits:

- `start`
- `normalize`
- `analyze`
- `write_plan`
- `persist`
- `complete`

Pre-brief and live workflows also emit trace events for their workflow stages.

## Audit Events

Every Lark adapter operation emits an audit event with:

- operation name,
- provider mode,
- sanitized input,
- read/write classification,
- dry-run flag,
- approval status,
- execution status,
- result summary or error message.

## Metrics

Operational metrics include:

- latency,
- trace event count,
- conversion count,
- tool call count,
- tool success count,
- approval count,
- failure count.

Live replay and benchmark metrics remain separate from operational metrics.

## Optional Export

OpenTelemetry, Phoenix, or similar systems are optional export targets. They are not runtime dependencies for V1.0.
