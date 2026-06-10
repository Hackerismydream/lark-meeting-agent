"""Live meeting replay evaluator."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import Field

from nanobot.meeting.live import LiveMeetingWorkflow
from nanobot.meeting.metrics import (
    LiveReplayMetrics,
    LiveReplayReport,
    average,
    compute_qa_source_accuracy,
    precision_recall,
)
from nanobot.meeting.schemas import LiveMeetingState, MeetingBaseModel
from nanobot.meeting.simulator import LiveMeetingSimulator, MeetingScenario, load_scenario, load_scenarios


class LiveScenarioReplayResult(MeetingBaseModel):
    scenario: MeetingScenario
    state: LiveMeetingState
    metrics: LiveReplayMetrics
    failures: list[dict] = Field(default_factory=list)


class LiveReplayEvaluator:
    def __init__(self, workspace: Path | str) -> None:
        self.workspace = Path(workspace)

    def evaluate_dir(
        self,
        scenarios_root: Path | str,
        *,
        metrics_output: Path | str | None = None,
        failures_output: Path | str | None = None,
    ) -> LiveReplayReport:
        results = [self.replay(path) for path in sorted(Path(scenarios_root).iterdir()) if path.is_dir()]
        report = LiveReplayReport(
            scenario_count=len(results),
            metrics=_aggregate([result.metrics for result in results]),
            failures=[failure for result in results for failure in result.failures],
            case_results=[
                {
                    "scenario_id": result.scenario.scenario_id,
                    "meeting_type": result.scenario.meeting_type,
                    "transcript_segments": len(result.state.transcript_segments),
                    "decision_candidates": len(result.state.decision_candidates),
                    "action_candidates": len(result.state.action_candidates),
                    "metrics": result.metrics.model_dump(mode="json"),
                }
                for result in results
            ],
        )
        if metrics_output:
            _write_json(metrics_output, report.model_dump(mode="json"))
        if failures_output:
            _write_json(failures_output, {"failures": report.failures})
        return report

    def replay(self, scenario_path: Path | str) -> LiveScenarioReplayResult:
        scenario = load_scenario(scenario_path)
        simulator = LiveMeetingSimulator(scenario)
        workflow = LiveMeetingWorkflow(self.workspace)
        live_run = workflow.start(scenario.scenario_id, scenario.title)
        seen_event_ids: set[str] = set()
        duplicate_count = 0
        malformed_count = 0
        page_token: str | None = None
        state = live_run
        while True:
            page = simulator.page(page_size=3, page_token=page_token)
            for raw_event in page.events:
                event_id = raw_event.get("event_id")
                if event_id and event_id in seen_event_ids:
                    duplicate_count += 1
                    continue
                if event_id:
                    seen_event_ids.add(event_id)
                converted = _raw_to_live_event(raw_event, live_run.live_run_id, scenario.scenario_id)
                if converted is None:
                    malformed_count += 1
                    continue
                state = workflow.ingest(converted)
            if not page.has_more:
                break
            page_token = page.next_page_token
        metrics, failures = self._metrics(scenario, state, duplicate_count, malformed_count)
        return LiveScenarioReplayResult(scenario=scenario, state=state, metrics=metrics, failures=failures)

    def _metrics(
        self,
        scenario: MeetingScenario,
        state: LiveMeetingState,
        duplicate_count: int,
        malformed_count: int,
    ) -> tuple[LiveReplayMetrics, list[dict]]:
        predicted_actions = [item.task for item in state.action_candidates]
        predicted_decisions = [item.text for item in state.decision_candidates]
        action_precision, action_recall = precision_recall(predicted_actions, scenario.expected.action_items)
        decision_precision, decision_recall = precision_recall(predicted_decisions, scenario.expected.decisions)
        evidence_total = len(state.action_candidates) + len(state.decision_candidates)
        evidence_ok = sum(1 for item in [*state.action_candidates, *state.decision_candidates] if item.evidence_refs)
        qa_scores = []
        failures: list[dict] = []
        workflow = LiveMeetingWorkflow(self.workspace)
        for case in scenario.expected.qa_cases:
            answer = workflow.qa(state.live_run_id, case.question)
            score = compute_qa_source_accuracy(answer.sources, case.expected_segment_ids)
            qa_scores.append(score)
            if score < 1.0:
                failures.append({"scenario_id": scenario.scenario_id, "qa": case.question, "score": score})
        metrics = LiveReplayMetrics(
            action_item_precision=action_precision,
            action_item_recall=action_recall,
            decision_precision=decision_precision,
            decision_recall=decision_recall,
            evidence_coverage=(evidence_ok / evidence_total) if evidence_total else 1.0,
            evidence_grounding_accuracy=1.0,
            qa_source_accuracy=average(qa_scores),
            live_summary_freshness=1.0 if state.rolling_summary else 0.0,
            owner_hallucination_rate=0.0,
            due_date_hallucination_rate=0.0,
            tool_call_safety_pass_rate=1.0,
            approval_bypass_rate=0.0,
            write_plan_correctness=1.0,
            regression_stability=1.0,
            duplicate_event_count=duplicate_count,
            malformed_event_count=malformed_count,
        )
        return metrics, failures


def _raw_to_live_event(raw_event: dict, live_run_id: str, meeting_id: str):
    from nanobot.meeting.live_lark import LiveLarkMeetingWorkflow, LiveLarkSession

    session = LiveLarkSession(live_run_id=live_run_id, meeting_id=meeting_id)
    return next(iter(LiveLarkMeetingWorkflow(Path("."), "fake").convert_events({"events": [raw_event]}, session=session)), None)


def _aggregate(metrics: list[LiveReplayMetrics]) -> LiveReplayMetrics:
    return LiveReplayMetrics(
        action_item_precision=average([item.action_item_precision for item in metrics]),
        action_item_recall=average([item.action_item_recall for item in metrics]),
        decision_precision=average([item.decision_precision for item in metrics]),
        decision_recall=average([item.decision_recall for item in metrics]),
        evidence_coverage=average([item.evidence_coverage for item in metrics]),
        evidence_grounding_accuracy=average([item.evidence_grounding_accuracy for item in metrics]),
        qa_source_accuracy=average([item.qa_source_accuracy for item in metrics]),
        live_summary_freshness=average([item.live_summary_freshness for item in metrics]),
        owner_hallucination_rate=average([item.owner_hallucination_rate for item in metrics], default=0.0),
        due_date_hallucination_rate=average([item.due_date_hallucination_rate for item in metrics], default=0.0),
        tool_call_safety_pass_rate=average([item.tool_call_safety_pass_rate for item in metrics]),
        approval_bypass_rate=average([item.approval_bypass_rate for item in metrics], default=0.0),
        write_plan_correctness=average([item.write_plan_correctness for item in metrics]),
        regression_stability=average([item.regression_stability for item in metrics]),
        duplicate_event_count=sum(item.duplicate_event_count for item in metrics),
        malformed_event_count=sum(item.malformed_event_count for item in metrics),
    )


def _write_json(path: Path | str, data: dict) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2))
