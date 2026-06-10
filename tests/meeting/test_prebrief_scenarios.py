from __future__ import annotations

from pathlib import Path

from nanobot.meeting.evals_lifecycle import LifecycleReplayEvaluator

SCENARIOS = Path("tests/fixtures/meeting/scenarios")


def test_prebrief_scenarios_have_sourced_context(tmp_path: Path) -> None:
    result = LifecycleReplayEvaluator(tmp_path).prebrief(SCENARIOS / "project_weekly")

    assert result.goal
    assert result.sections
    assert any(section.sources or section.bullets for section in result.sections)
