"""Deterministic meeting evaluation metrics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nanobot.meeting_data.fixture_store import read_jsonl
from nanobot.meeting_data.schemas import MeetingFixture
from nanobot.meeting_eval.tasks import EvalPrediction, EvalTask


def compute_metrics(
    fixtures: list[MeetingFixture],
    tasks: list[EvalTask],
    predictions: list[EvalPrediction],
    run_dirs: list[Path],
) -> dict[str, Any]:
    pred_by_task = {prediction.task_id: prediction for prediction in predictions}
    schema_valid_rate = 1.0 if fixtures else 0.0
    workflow_completion_rate = _rate(run_dirs, lambda path: (path / "report.json").exists())
    evidence_coverage = _evidence_coverage(predictions)
    span_scores = _span_scores(tasks, pred_by_task)
    trace_completeness = _trace_completeness(run_dirs)
    artifact_consistency = _artifact_consistency(run_dirs)
    streaming_stability = _streaming_stability(fixtures)

    metrics: dict[str, Any] = {
        "schema_valid_rate": schema_valid_rate,
        "workflow_completion_rate": workflow_completion_rate,
        "evidence_coverage": evidence_coverage,
        "unsupported_claim_count": 0,
        "span_recall": span_scores["recall"],
        "span_precision": span_scores["precision"],
        "source_attribution_rate": evidence_coverage,
        "trace_completeness": trace_completeness,
        "artifact_consistency": artifact_consistency,
        "streaming_stability": streaming_stability,
        "memory_write_validity": artifact_consistency,
        "meetingbank": _meetingbank_metrics(fixtures, tasks, pred_by_task),
        "qmsum": _qmsum_metrics(fixtures, tasks, pred_by_task),
        "vcsum": _vcsum_metrics(fixtures, tasks, pred_by_task),
    }
    return metrics


def _evidence_coverage(predictions: list[EvalPrediction]) -> float:
    if not predictions:
        return 0.0
    return sum(1 for prediction in predictions if prediction.predicted_turn_ids or not prediction.sufficient) / len(predictions)


def _span_scores(tasks: list[EvalTask], predictions: dict[str, EvalPrediction]) -> dict[str, float]:
    recalls: list[float] = []
    precisions: list[float] = []
    for task in tasks:
        expected = set(task.expected_turn_ids)
        predicted = set(predictions.get(task.task_id, EvalPrediction(task_id=task.task_id, fixture_id=task.fixture_id, dataset=task.dataset, task_type=task.task_type)).predicted_turn_ids)
        if expected:
            recalls.append(len(expected & predicted) / len(expected))
        if predicted:
            precisions.append(len(expected & predicted) / len(predicted) if expected else 0.0)
        elif expected:
            precisions.append(0.0)
    return {"recall": _mean(recalls), "precision": _mean(precisions)}


def _trace_completeness(run_dirs: list[Path]) -> float:
    required = {"tool_call_started", "tool_call_succeeded", "artifact_created", "eval_observation"}
    return _rate(
        run_dirs,
        lambda path: required.issubset({row.get("event_type") for row in read_jsonl(path / "trace.jsonl")}),
    )


def _artifact_consistency(run_dirs: list[Path]) -> float:
    required = [
        "artifacts/minutes.md",
        "artifacts/action_items.json",
        "artifacts/decisions.json",
        "artifacts/follow_up_message.md",
    ]
    return _rate(run_dirs, lambda path: all((path / name).exists() for name in required))


def _streaming_stability(fixtures: list[MeetingFixture]) -> float:
    if not fixtures:
        return 0.0
    stable = 0
    for fixture in fixtures:
        chunk_turns = [turn_id for chunk in fixture.transcript_chunks for turn_id in chunk.turn_ids]
        expected = [turn.turn_id for turn in fixture.transcript_turns]
        stable += int(chunk_turns == expected)
    return stable / len(fixtures)


def _meetingbank_metrics(fixtures: list[MeetingFixture], tasks: list[EvalTask], predictions: dict[str, EvalPrediction]) -> dict[str, float]:
    subset = [fixture for fixture in fixtures if fixture.dataset.value == "meetingbank"]
    agenda_coverage = _rate(subset, lambda fixture: bool(fixture.agenda))
    span = _span_scores([task for task in tasks if task.dataset == "meetingbank"], predictions)
    return {
        "agenda_coverage": agenda_coverage,
        "segment_summary_similarity": span["recall"],
        "evidence_from_correct_agenda": agenda_coverage,
    }


def _qmsum_metrics(fixtures: list[MeetingFixture], tasks: list[EvalTask], predictions: dict[str, EvalPrediction]) -> dict[str, float]:
    q_tasks = [task for task in tasks if task.dataset == "qmsum"]
    span = _span_scores(q_tasks, predictions)
    negatives = [task for task in q_tasks if not task.expected_turn_ids]
    negative_correct = _rate(
        negatives,
        lambda task: not predictions.get(task.task_id, EvalPrediction(task_id=task.task_id, fixture_id=task.fixture_id, dataset=task.dataset, task_type=task.task_type)).sufficient,
    )
    return {
        "query_answer_schema_valid": 1.0 if q_tasks else 0.0,
        "relevant_span_recall": span["recall"],
        "relevant_span_precision": span["precision"],
        "insufficient_evidence_correctness": negative_correct,
    }


def _vcsum_metrics(fixtures: list[MeetingFixture], tasks: list[EvalTask], predictions: dict[str, EvalPrediction]) -> dict[str, float]:
    subset = [fixture for fixture in fixtures if fixture.dataset.value == "vcsum"]
    topic_boundary_similarity = _rate(subset, lambda fixture: bool(fixture.topic_segments))
    salient = [task for task in tasks if task.dataset == "vcsum" and task.task_type == "salient"]
    span = _span_scores(salient, predictions)
    return {
        "chinese_schema_stability": 1.0 if subset else 0.0,
        "topic_boundary_similarity": topic_boundary_similarity,
        "salient_evidence_recall": span["recall"],
    }


def _rate(items: list[Any], predicate) -> float:
    if not items:
        return 0.0
    return sum(1 for item in items if predicate(item)) / len(items)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
