from __future__ import annotations

from nanobot.meeting_eval.metrics import compute_metrics
from nanobot.meeting_eval.tasks import EvalPrediction, EvalTask
from tests.meeting_data.test_fixture_schema import valid_fixture


def test_grounding_metrics_compute_span_precision_and_recall() -> None:
    task = EvalTask(
        task_id="task-1",
        fixture_id="qmsum-fixture-1",
        dataset="qmsum",
        task_type="qa",
        expected_turn_ids=["turn-0002"],
    )
    prediction = EvalPrediction(
        task_id="task-1",
        fixture_id="qmsum-fixture-1",
        dataset="qmsum",
        task_type="qa",
        predicted_turn_ids=["turn-0002"],
    )

    metrics = compute_metrics([valid_fixture()], [task], [prediction], [])

    assert metrics["span_recall"] == 1.0
    assert metrics["span_precision"] == 1.0
    assert metrics["source_attribution_rate"] == 1.0
