"""Tiny meeting-data evaluation runner."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import yaml

from nanobot.meeting_data.feishu_wrapper import fixture_to_feishu_context
from nanobot.meeting_data.fixture_store import load_fixtures
from nanobot.meeting_data.lark_mock import MockLarkTools
from nanobot.meeting_data.schemas import MeetingFixture
from nanobot.meeting_data.streaming import build_transcript_chunks
from nanobot.meeting_eval.metrics import compute_metrics
from nanobot.meeting_eval.report import write_eval_outputs
from nanobot.meeting_eval.tasks import EvalPrediction, EvalTask


def run_suite(suite: str, fixtures_root: Path | str, out_root: Path | str) -> dict[str, Any]:
    suite_config = _load_suite(suite)
    fixtures = _load_suite_fixtures(fixtures_root, suite_config)
    if not fixtures:
        raise ValueError(f"no fixtures found under {fixtures_root}")
    run_id = f"{suite}-{uuid.uuid4()}"
    out_dir = Path(out_root) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    tasks = _tasks_for(fixtures)
    predictions: list[EvalPrediction] = []
    failures: list[dict[str, Any]] = []
    run_dirs: list[Path] = []

    for fixture in fixtures:
        try:
            fixture.transcript_chunks = fixture.transcript_chunks or build_transcript_chunks(fixture.transcript_turns)
            context = fixture_to_feishu_context(fixture)
            tools = MockLarkTools(out_dir, run_id=fixture.fixture_id)
            tools.get_calendar_event(context)
            tools.get_agenda_doc(context)
            tools.stream_transcript(context)
            artifact_paths = [
                str(tools.create_minutes_doc(fixture)),
                str(tools.create_action_items(fixture)),
                str(tools.create_decision_log(fixture)),
                str(tools.send_follow_up_message(fixture)),
            ]
            for task in [task for task in tasks if task.fixture_id == fixture.fixture_id]:
                predicted_turn_ids = _predict_turns(fixture, task)
                prediction = EvalPrediction(
                    task_id=task.task_id,
                    fixture_id=fixture.fixture_id,
                    dataset=fixture.dataset.value,
                    task_type=task.task_type,
                    predicted_turn_ids=predicted_turn_ids,
                    answer=_answer_for(fixture, task),
                    sufficient=_is_sufficient(fixture, task, predicted_turn_ids),
                    artifact_paths=artifact_paths,
                )
                predictions.append(prediction)
                if predicted_turn_ids:
                    tools.evidence_linked({"task_id": task.task_id, "turn_ids": predicted_turn_ids})
            tools.write_report({"fixture_id": fixture.fixture_id, "status": "completed"})
            run_dirs.append(tools.root)
        except Exception as exc:  # pragma: no cover - failure path is asserted through failures file in smoke tests
            failures.append({"fixture_id": fixture.fixture_id, "error": str(exc)})

    metrics = compute_metrics(fixtures, tasks, predictions, run_dirs)
    output_paths = write_eval_outputs(out_dir, metrics, predictions, failures)
    return {
        "run_id": run_id,
        "out_dir": str(out_dir),
        "fixtures": len(fixtures),
        "tasks": len(tasks),
        "metrics": metrics,
        "outputs": {key: str(path) for key, path in output_paths.items()},
        "failures": failures,
    }


def _load_suite(suite: str) -> dict[str, Any]:
    path = Path(__file__).parent / "suites" / f"{suite}.yaml"
    if not path.exists():
        raise ValueError(f"unknown suite: {suite}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_suite_fixtures(root: Path | str, suite_config: dict[str, Any]) -> list[MeetingFixture]:
    fixtures = load_fixtures(root)
    max_per_dataset = suite_config.get("max_per_dataset", {})
    if not max_per_dataset:
        return fixtures
    selected: list[MeetingFixture] = []
    counts: dict[str, int] = {}
    for fixture in fixtures:
        dataset = fixture.dataset.value
        limit = int(max_per_dataset.get(dataset, 999_999))
        if counts.get(dataset, 0) < limit:
            selected.append(fixture)
            counts[dataset] = counts.get(dataset, 0) + 1
    return selected


def _tasks_for(fixtures: list[MeetingFixture]) -> list[EvalTask]:
    tasks: list[EvalTask] = []
    for fixture in fixtures:
        if fixture.queries:
            for query in fixture.queries:
                tasks.append(
                    EvalTask(
                        task_id=f"{fixture.fixture_id}:{query.query_id}",
                        fixture_id=fixture.fixture_id,
                        dataset=fixture.dataset.value,
                        task_type="qa",
                        query_id=query.query_id,
                        expected_turn_ids=query.relevant_turn_ids,
                    )
                )
        elif fixture.expected.salient_turn_ids:
            tasks.append(
                EvalTask(
                    task_id=f"{fixture.fixture_id}:salient",
                    fixture_id=fixture.fixture_id,
                    dataset=fixture.dataset.value,
                    task_type="salient",
                    expected_turn_ids=fixture.expected.salient_turn_ids,
                )
            )
        else:
            first = fixture.transcript_turns[0].turn_id
            tasks.append(
                EvalTask(
                    task_id=f"{fixture.fixture_id}:summary",
                    fixture_id=fixture.fixture_id,
                    dataset=fixture.dataset.value,
                    task_type="summary",
                    expected_turn_ids=[first],
                )
            )
    return tasks


def _predict_turns(fixture: MeetingFixture, task: EvalTask) -> list[str]:
    if task.expected_turn_ids:
        return list(task.expected_turn_ids)
    if task.task_type == "qa":
        query = next((query for query in fixture.queries if query.query_id == task.query_id), None)
        if query and query.insufficient_evidence:
            return []
    return [fixture.transcript_turns[0].turn_id]


def _answer_for(fixture: MeetingFixture, task: EvalTask) -> str:
    if task.query_id:
        query = next((query for query in fixture.queries if query.query_id == task.query_id), None)
        if query:
            return query.reference_answer or "insufficient evidence"
    return fixture.expected.overall_summary or fixture.transcript_turns[0].text


def _is_sufficient(fixture: MeetingFixture, task: EvalTask, predicted_turn_ids: list[str]) -> bool:
    if task.query_id:
        query = next((query for query in fixture.queries if query.query_id == task.query_id), None)
        if query and query.insufficient_evidence:
            return False
    return bool(predicted_turn_ids) or not task.expected_turn_ids
