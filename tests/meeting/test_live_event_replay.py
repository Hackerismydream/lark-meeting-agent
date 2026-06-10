from __future__ import annotations

from pathlib import Path

from nanobot.meeting.evals_live import LiveReplayEvaluator

SCENARIOS = Path("tests/fixtures/meeting/scenarios")


def test_live_replay_runs_all_scenarios_and_writes_reports(tmp_path: Path) -> None:
    report_path = tmp_path / "live_metrics.json"
    failures_path = tmp_path / "live_failures.json"

    report = LiveReplayEvaluator(tmp_path).evaluate_dir(
        SCENARIOS,
        metrics_output=report_path,
        failures_output=failures_path,
    )

    assert report.scenario_count == 8
    assert report.metrics.evidence_coverage == 1.0
    assert report.metrics.qa_source_accuracy == 1.0
    assert report.metrics.approval_bypass_rate == 0.0
    assert report_path.exists()
    assert failures_path.exists()


def test_live_replay_deduplicates_event_ids(tmp_path: Path) -> None:
    result = LiveReplayEvaluator(tmp_path).replay(SCENARIOS / "tech_review")
    segment_ids = [segment.segment_id for segment in result.state.transcript_segments]

    assert len(segment_ids) == len(set(segment_ids))
    assert result.metrics.duplicate_event_count >= 1
