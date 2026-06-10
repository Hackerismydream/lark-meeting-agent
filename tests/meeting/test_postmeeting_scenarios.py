from __future__ import annotations

from pathlib import Path

from nanobot.meeting.evals_lifecycle import LifecycleReplayEvaluator

SCENARIOS = Path("tests/fixtures/meeting/scenarios")


def test_postmeeting_scenario_generates_dry_run_write_plan(tmp_path: Path) -> None:
    result = LifecycleReplayEvaluator(tmp_path).postmeeting(SCENARIOS / "customer_poc_review")

    assert result.write_plan
    assert result.write_plan.operations
    assert all(operation.execution_status.value != "completed" for operation in result.write_plan.operations)
