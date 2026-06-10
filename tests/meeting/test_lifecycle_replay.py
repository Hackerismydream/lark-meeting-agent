from __future__ import annotations

from pathlib import Path

from nanobot.meeting.evals_lifecycle import LifecycleReplayEvaluator

SCENARIOS = Path("tests/fixtures/meeting/scenarios")


def test_lifecycle_replay_runs_prebrief_live_and_postmeeting(tmp_path: Path) -> None:
    report = LifecycleReplayEvaluator(tmp_path).evaluate_dir(SCENARIOS)

    assert report.scenario_count == 8
    assert report.prebrief_pass_rate == 1.0
    assert report.live_pass_rate == 1.0
    assert report.postmeeting_pass_rate == 1.0
