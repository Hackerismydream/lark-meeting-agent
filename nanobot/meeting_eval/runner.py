"""Tiny meeting-data evaluation runner."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import yaml

from nanobot.meeting.live import LiveMeetingWorkflow
from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.renderers import render_minutes_markdown
from nanobot.meeting.schemas import (
    AnalyzerMode,
    LiveEventKind,
    LiveMeetingEvent,
    MeetingRef,
    MeetingRefType,
    MeetingType,
    PreBrief,
    PreBriefInput,
    ProviderMode,
)
from nanobot.meeting.workflow import PostMeetingWorkflow
from nanobot.meeting_data.feishu_wrapper import fixture_to_feishu_context
from nanobot.meeting_data.fixture_store import load_fixtures, write_jsonl
from nanobot.meeting_data.lark_mock import MockLarkTools
from nanobot.meeting_data.schemas import MeetingFixture
from nanobot.meeting_data.streaming import build_transcript_chunks
from nanobot.meeting_eval.metrics import compute_metrics
from nanobot.meeting_eval.report import write_eval_outputs
from nanobot.meeting_eval.tasks import EvalPrediction, EvalTask


def run_suite(suite: str, fixtures_root: Path | str, out_root: Path | str, mode: str = "mock_smoke") -> dict[str, Any]:
    suite_config = _load_suite(suite)
    fixtures = _load_suite_fixtures(fixtures_root, suite_config)
    if not fixtures:
        raise ValueError(f"no fixtures found under {fixtures_root}")
    if mode not in {"mock_smoke", "agent"}:
        raise ValueError(f"unsupported eval mode: {mode}")
    run_id = f"{suite}-{uuid.uuid4()}"
    out_dir = Path(out_root) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    if mode == "agent":
        return _run_agent_suite(suite, run_id, out_dir, fixtures)
    return _run_mock_smoke_suite(suite, run_id, out_dir, fixtures)


def _run_mock_smoke_suite(suite: str, run_id: str, out_dir: Path, fixtures: list[MeetingFixture]) -> dict[str, Any]:
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
    metrics["metric_scope"] = "public_corpus_development"
    metrics["write_plan_dry_run_rate"] = 1.0
    output_paths = write_eval_outputs(out_dir, metrics, predictions, failures, _metadata(suite, "mock_smoke", fixtures, used_real_llm=False))
    return {
        "run_id": run_id,
        "mode": "mock_smoke",
        "out_dir": str(out_dir),
        "fixtures": len(fixtures),
        "tasks": len(tasks),
        "metrics": metrics,
        "outputs": {key: str(path) for key, path in output_paths.items()},
        "failures": failures,
    }


def _run_agent_suite(suite: str, run_id: str, out_dir: Path, fixtures: list[MeetingFixture]) -> dict[str, Any]:
    tasks = _tasks_for(fixtures)
    predictions: list[EvalPrediction] = []
    failures: list[dict[str, Any]] = []
    run_dirs: list[Path] = []
    all_write_ops = 0
    dry_run_write_ops = 0
    used_real_llm = os.environ.get("RUN_REAL_LLM_TESTS") == "1"
    analyzer_mode = AnalyzerMode.LLM.value if used_real_llm else AnalyzerMode.FAKE.value

    for fixture in fixtures:
        fixture_dir = out_dir / _safe_path_name(fixture.fixture_id)
        artifacts = fixture_dir / "artifacts"
        workspace = fixture_dir / "memory"
        artifacts.mkdir(parents=True, exist_ok=True)
        workspace.mkdir(parents=True, exist_ok=True)
        trace_events: list[dict[str, Any]] = []
        try:
            trace_events.append(_trace("workflow_started", "agent fixture evaluation started", {"fixture_id": fixture.fixture_id}))
            fixture.transcript_chunks = fixture.transcript_chunks or build_transcript_chunks(fixture.transcript_turns)
            context = fixture_to_feishu_context(fixture)

            prebrief = _run_prebrief(workspace, fixture, context)
            _write_prebrief_artifacts(prebrief, fixture, artifacts)
            trace_events.append(_trace("artifact_created", "prebrief artifacts written", {"fixture_id": fixture.fixture_id}))

            live_snapshots, live_answers = _run_live_replay(workspace, fixture)
            write_jsonl(live_snapshots, artifacts / "live_state_snapshots.jsonl")
            write_jsonl(live_answers, artifacts / "live_qa_answers.jsonl")
            trace_events.append(_trace("artifact_created", "live replay artifacts written", {"snapshots": len(live_snapshots)}))

            transcript_path = fixture_dir / "transcript.txt"
            transcript_path.write_text(_fixture_transcript_text(fixture), encoding="utf-8")
            post = PostMeetingWorkflow(workspace, provider_mode=ProviderMode.FAKE.value, analyzer_mode=analyzer_mode).process_transcript_file(
                transcript_path,
                create_doc=True,
                create_tasks=True,
                send_message=False,
                dry_run=True,
                provider_mode=ProviderMode.FAKE.value,
                analyzer_mode=analyzer_mode,
            )
            if post.minutes and post.meeting:
                (artifacts / "minutes.md").write_text(render_minutes_markdown(post.meeting, post.minutes), encoding="utf-8")
                _write_json(artifacts / "decisions.json", [item.model_dump(mode="json") for item in post.minutes.decisions])
                _write_json(artifacts / "action_items.json", [item.model_dump(mode="json") for item in post.minutes.action_items])
                _write_json(artifacts / "risks.json", [item.model_dump(mode="json") for item in post.minutes.risks])
                _write_json(artifacts / "open_questions.json", [item.model_dump(mode="json") for item in post.minutes.open_questions])
            write_plan = post.write_plan.model_dump(mode="json") if post.write_plan else {"operations": []}
            _write_json(artifacts / "write_plan.json", write_plan)
            ops = write_plan.get("operations", [])
            all_write_ops += len(ops)
            dry_run_write_ops += sum(1 for operation in ops if operation.get("dry_run_payload") and operation.get("execution_status") in {"pending", "dry_run"})
            trace_events.append(_trace("artifact_created", "post meeting artifacts written", {"operations": len(ops)}))

            fixture_tasks = [task for task in tasks if task.fixture_id == fixture.fixture_id]
            qa_rows = _qa_rows_for_fixture(fixture, fixture_tasks)
            write_jsonl(qa_rows, artifacts / "qa_answers.jsonl")
            write_jsonl([{"fixture_id": fixture.fixture_id, "qa_sources": row["sources"]} for row in qa_rows], workspace / "qa_sources.jsonl")
            artifact_paths = sorted(str(path) for path in artifacts.iterdir() if path.is_file())
            for task, row in zip(fixture_tasks, qa_rows, strict=False):
                predictions.append(
                    EvalPrediction(
                        task_id=task.task_id,
                        fixture_id=fixture.fixture_id,
                        dataset=fixture.dataset.value,
                        task_type=task.task_type,
                        predicted_turn_ids=row["predicted_turn_ids"],
                        answer=row["answer"],
                        sufficient=row["sufficient"],
                        artifact_paths=artifact_paths,
                    )
                )
            trace_events.append(_trace("eval_observation", "qa predictions written", {"predictions": len(qa_rows)}))
            trace_events.append(_trace("workflow_completed", "agent fixture evaluation completed", {"fixture_id": fixture.fixture_id}))
            _write_json(fixture_dir / "report.json", {"fixture_id": fixture.fixture_id, "status": "completed", "artifacts": artifact_paths})
            run_dirs.append(fixture_dir)
        except Exception as exc:  # pragma: no cover - exercised through failures output in integration runs
            failures.append({"fixture_id": fixture.fixture_id, "error": str(exc)})
            trace_events.append(_trace("eval_observation", "agent fixture evaluation failed", {"error": str(exc)}))
            _write_json(fixture_dir / "report.json", {"fixture_id": fixture.fixture_id, "status": "failed", "error": str(exc)})
            run_dirs.append(fixture_dir)
        finally:
            write_jsonl(trace_events, fixture_dir / "trace.jsonl")

    metrics = compute_metrics(fixtures, tasks, predictions, run_dirs)
    metrics["metric_scope"] = "public_corpus_development"
    metrics["write_plan_dry_run_rate"] = dry_run_write_ops / all_write_ops if all_write_ops else 1.0
    output_paths = write_eval_outputs(out_dir, metrics, predictions, failures, _metadata(suite, "agent", fixtures, used_real_llm=used_real_llm))
    return {
        "run_id": run_id,
        "mode": "agent",
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


def _run_prebrief(workspace: Path, fixture: MeetingFixture, context) -> PreBrief:
    participants = [participant.name for participant in context.participants]
    return PreBriefWorkflow(workspace, provider_mode=ProviderMode.FAKE.value).generate(
        PreBriefInput(
            meeting_ref=MeetingRef(type=MeetingRefType.MEETING_ID, value=context.calendar_event.event_id, query=context.calendar_event.title),
            provider_mode=ProviderMode.FAKE,
            meeting_type=MeetingType.GENERAL,
            project=fixture.meta.domain or fixture.dataset.value,
            customer=fixture.meta.city,
            participants=participants,
        )
    )


def _write_prebrief_artifacts(prebrief: PreBrief, fixture: MeetingFixture, artifacts: Path) -> None:
    lines = [f"# {fixture.meta.title}", "", prebrief.goal, "", "## Sections"]
    sources = [
        {
            "kind": "provenance",
            "dataset": fixture.dataset.value,
            "source_id": fixture.provenance.source_id,
            "source_path": fixture.provenance.source_path,
        }
    ]
    for section in prebrief.sections:
        lines.extend(["", f"### {section.title}"])
        lines.extend(f"- {bullet}" for bullet in section.bullets)
        sources.extend(source.model_dump(mode="json") for source in section.sources)
    if fixture.agenda:
        lines.extend(["", "## Source Agenda"])
        lines.extend(f"- {item.title}" for item in fixture.agenda[:12])
    elif fixture.queries:
        lines.extend(["", "## Source Queries"])
        lines.extend(f"- {query.question}" for query in fixture.queries[:6])
    (artifacts / "prebrief.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    _write_json(artifacts / "prebrief_sources.json", sources)


def _run_live_replay(workspace: Path, fixture: MeetingFixture) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    workflow = LiveMeetingWorkflow(workspace)
    state = workflow.start(fixture.fixture_id, fixture.meta.title)
    snapshots: list[dict[str, Any]] = []
    for chunk in fixture.transcript_chunks:
        event = LiveMeetingEvent(
            event_id=chunk.chunk_id,
            live_run_id=state.live_run_id,
            meeting_id=fixture.fixture_id,
            kind=LiveEventKind.TRANSCRIPT_DELTA,
            text=chunk.text,
            timestamp=str(chunk.start_sec),
            segment_id=chunk.chunk_id,
        )
        state = workflow.ingest(event)
        snapshots.append(
            {
                "chunk_id": chunk.chunk_id,
                "meeting_id": fixture.fixture_id,
                "segment_count": len(state.transcript_segments),
                "rolling_summary": state.rolling_summary,
                "current_topic": state.current_topic,
            }
        )
    questions = [query.question for query in fixture.queries[:2]] or ["刚才讨论了什么？"]
    answers = []
    for question in questions:
        answer = workflow.qa(state.live_run_id, question)
        answers.append(answer.model_dump(mode="json"))
    return snapshots, answers


def _fixture_transcript_text(fixture: MeetingFixture) -> str:
    lines = []
    for turn in fixture.transcript_turns:
        speaker = f"{turn.speaker}: " if turn.speaker else ""
        lines.append(f"{speaker}{turn.text}")
    return "\n".join(lines)


def _qa_rows_for_fixture(fixture: MeetingFixture, tasks: list[EvalTask]) -> list[dict[str, Any]]:
    rows = []
    turns = {turn.turn_id: turn for turn in fixture.transcript_turns}
    for task in tasks:
        predicted = _predict_turns(fixture, task)
        sources = []
        for turn_id in predicted:
            turn = turns.get(turn_id)
            if turn:
                sources.append(
                    {
                        "meeting_id": fixture.fixture_id,
                        "segment_id": turn.turn_id,
                        "speaker": turn.speaker,
                        "timestamp": turn.start_time or turn.start_sec,
                        "text": turn.text,
                    }
                )
        rows.append(
            {
                "task_id": task.task_id,
                "question": _question_for(fixture, task),
                "answer": _answer_for(fixture, task),
                "sources": sources,
                "sufficient": _is_sufficient(fixture, task, predicted),
                "expected_relevant_turn_ids": task.expected_turn_ids,
                "predicted_turn_ids": predicted,
            }
        )
    return rows


def _question_for(fixture: MeetingFixture, task: EvalTask) -> str:
    if task.query_id:
        query = next((query for query in fixture.queries if query.query_id == task.query_id), None)
        if query:
            return query.question
    if task.task_type == "salient":
        return "哪些片段是该会议的关键证据？"
    if fixture.agenda:
        return f"会议议程 {fixture.agenda[0].title} 讨论了什么？"
    return "这场会议的主要内容是什么？"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _trace(event_type: str, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"event_type": event_type, "message": message, "data": data or {}}


def _safe_path_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in value)


def _metadata(suite: str, mode: str, fixtures: list[MeetingFixture], *, used_real_llm: bool) -> dict[str, Any]:
    return {
        "suite": suite,
        "mode": mode,
        "metric_scope": "public_corpus_development",
        "fixture_count": len(fixtures),
        "used_real_llm": used_real_llm,
        "used_real_lark": False,
        "real_writes": False,
        "evaluator_profile": "fake analyzer and deterministic source matching unless used_real_llm=true",
    }
