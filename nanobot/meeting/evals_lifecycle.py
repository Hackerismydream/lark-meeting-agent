"""Lifecycle scenario replay evaluator."""

from __future__ import annotations

from pathlib import Path

from nanobot.meeting.evals_live import LiveReplayEvaluator
from nanobot.meeting.metrics import LifecycleReplayReport
from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.schemas import MeetingRef, MeetingRefType, MeetingType, PreBriefInput, ProcessMeetingInput
from nanobot.meeting.simulator import load_scenario
from nanobot.meeting.workflow import PostMeetingWorkflow


class LifecycleReplayEvaluator:
    def __init__(self, workspace: Path | str) -> None:
        self.workspace = Path(workspace)

    def evaluate_dir(self, scenarios_root: Path | str) -> LifecycleReplayReport:
        paths = [path for path in sorted(Path(scenarios_root).iterdir()) if path.is_dir()]
        prebrief_ok = live_ok = post_ok = 0
        failures: list[dict] = []
        for path in paths:
            scenario_id = path.name
            try:
                self.prebrief(path)
                prebrief_ok += 1
            except Exception as exc:
                failures.append({"scenario_id": scenario_id, "stage": "prebrief", "error": str(exc)})
            try:
                LiveReplayEvaluator(self.workspace).replay(path)
                live_ok += 1
            except Exception as exc:
                failures.append({"scenario_id": scenario_id, "stage": "live", "error": str(exc)})
            try:
                self.postmeeting(path)
                post_ok += 1
            except Exception as exc:
                failures.append({"scenario_id": scenario_id, "stage": "postmeeting", "error": str(exc)})
        total = len(paths) or 1
        return LifecycleReplayReport(
            scenario_count=len(paths),
            prebrief_pass_rate=prebrief_ok / total,
            live_pass_rate=live_ok / total,
            postmeeting_pass_rate=post_ok / total,
            failures=failures,
        )

    def prebrief(self, scenario_path: Path | str):
        scenario = load_scenario(scenario_path)
        meeting_type = _meeting_type(scenario.meeting_type)
        return PreBriefWorkflow(self.workspace, "fake").generate(
            PreBriefInput(
                meeting_ref=MeetingRef(type=MeetingRefType.LATEST_ENDED, query=scenario.title),
                provider_mode="fake",
                meeting_type=meeting_type,
                project=scenario.project,
                customer=scenario.customer,
                participants=[participant.display_name for participant in scenario.participants],
            )
        )

    def postmeeting(self, scenario_path: Path | str):
        scenario = load_scenario(scenario_path)
        transcript_path = self.workspace / f"{scenario.scenario_id}.transcript.txt"
        transcript_path.write_text(scenario.transcript_text)
        return PostMeetingWorkflow(self.workspace, "fake", "fake").process(
            ProcessMeetingInput(
                meeting_ref=MeetingRef(type=MeetingRefType.TRANSCRIPT_FILE, value=str(transcript_path)),
                provider_mode="fake",
                analyzer_mode="fake",
                create_doc=True,
                create_tasks=True,
                send_message=False,
                dry_run=True,
            )
        )


def _meeting_type(value: str) -> MeetingType:
    mapping = {
        "customer_poc_review": MeetingType.CUSTOMER_MEETING,
        "project_weekly": MeetingType.PROJECT_SYNC,
        "requirement_review": MeetingType.REQUIREMENT_REVIEW,
        "tech_review": MeetingType.TECHNICAL_REVIEW,
        "incident_review": MeetingType.INCIDENT_REVIEW,
        "one_on_one": MeetingType.ONE_ON_ONE,
        "sales_cs_followup": MeetingType.CUSTOMER_MEETING,
        "long_project_retrospective": MeetingType.PROJECT_SYNC,
    }
    return mapping.get(value, MeetingType.GENERAL)
