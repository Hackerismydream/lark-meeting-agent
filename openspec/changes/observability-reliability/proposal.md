# Proposal: Observability and Reliability

## Intent

Implement V1.0 phase `observability-reliability` for Lark Meeting Agent.

## Problem

The project is evolving from a local meeting-agent MVP into a V1.0 production-grade engineering release. This phase addresses:

- Every workflow node emits trace event.
- Every Lark tool call emits audit event.
- Error taxonomy covers permission, gray, missing transcript, unknown event, malformed output, approval mismatch, provider mismatch.
- Metrics include latency, event count, conversion count, tool success, approval count, failures.
- OpenTelemetry/Phoenix documented as optional, not mandatory dependency.

## Scope

This change covers:

- Every workflow node emits trace event.
- Every Lark tool call emits audit event.
- Error taxonomy covers permission, gray, missing transcript, unknown event, malformed output, approval mismatch, provider mismatch.
- Metrics include latency, event count, conversion count, tool success, approval count, failures.
- OpenTelemetry/Phoenix documented as optional, not mandatory dependency.

## Non-goals

- Do not implement unrelated phases.
- Do not require real Lark credentials for automated tests.
- Do not require real LLM keys for automated tests.
- Do not bypass `LarkToolAdapter`.
- Do not perform unapproved writes.
- Do not fabricate real smoke results.

## Success Criteria

- Trace JSONL can reconstruct a run.
- Metrics report generated for replay and smoke.
- Error classes map to user-safe messages.
- No secret leakage in traces.
