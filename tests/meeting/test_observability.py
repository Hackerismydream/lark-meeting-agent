from __future__ import annotations

import json
from pathlib import Path

from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.metrics import OperationalMetrics, build_operational_metrics
from nanobot.meeting.tracing import TraceReader
from nanobot.meeting.workflow import PostMeetingWorkflow
from nanobot.meeting.schemas import ApprovalStatus

FIXTURE = Path("tests/fixtures/meeting/transcripts/sample_project_sync.txt")


def test_postmeeting_trace_json_can_reconstruct_run(tmp_path: Path) -> None:
    result = PostMeetingWorkflow(tmp_path, provider_mode="fake", analyzer_mode="fake").process_transcript_file(
        FIXTURE,
        create_doc=True,
        create_tasks=True,
        dry_run=True,
    )

    trace = TraceReader(tmp_path).load(result.run_id)
    stages = [event.stage for event in trace.events]

    assert trace.run_id == result.run_id
    assert stages == ["start", "normalize", "analyze", "write_plan", "persist", "complete"]
    assert "sk-secret" not in json.dumps(trace.model_dump(mode="json"))


def test_operational_metrics_from_trace_and_audit_events(tmp_path: Path) -> None:
    adapter = LarkToolAdapter.fake(tmp_path)
    adapter.execute("vc.search", {"query": "Alpha"})
    adapter.execute("docs.create", {"title": "纪要", "markdown": "# 内容"}, dry_run=True)
    adapter.execute("docs.create", {"title": "纪要", "markdown": "# 内容"}, dry_run=False, approval_status=ApprovalStatus.APPROVED)

    result = PostMeetingWorkflow(tmp_path, provider_mode="fake", analyzer_mode="fake").process_transcript_file(FIXTURE)
    trace = TraceReader(tmp_path).load(result.run_id)
    metrics = build_operational_metrics(trace=trace, audit_events=adapter.audit_events)

    assert isinstance(metrics, OperationalMetrics)
    assert metrics.event_count == 6
    assert metrics.tool_call_count == 3
    assert metrics.tool_success_count == 3
    assert metrics.approval_count == 1
    assert metrics.failure_count == 0
    assert metrics.latency_ms >= 0


def test_trace_redacts_secret_values(tmp_path: Path) -> None:
    result = PostMeetingWorkflow(tmp_path, provider_mode="fake", analyzer_mode="fake").process_transcript_file(
        FIXTURE,
        create_doc=False,
        create_tasks=False,
        dry_run=True,
    )
    trace_path = tmp_path / ".lark_meeting_agent" / "traces" / f"{result.run_id}.json"
    text = trace_path.read_text()

    assert "access_token" not in text.lower()
    assert "Bearer sk-" not in text
