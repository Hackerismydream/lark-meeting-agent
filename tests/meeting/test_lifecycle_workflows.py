from __future__ import annotations

import json
from pathlib import Path

import pytest

from nanobot.agent.tools.lark_meeting import LarkMeetingTool
from nanobot.meeting.evals import LifecycleEvaluator
from nanobot.meeting.live import LiveMeetingWorkflow
from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.retrieval import MeetingRetrievalEngine
from nanobot.meeting.schemas import (
    EntityMemory,
    EvidenceRef,
    LiveEventKind,
    LiveMeetingEvent,
    MemoryEntityType,
    MeetingRef,
    MeetingRefType,
    MeetingType,
    PreBriefInput,
    RetrievalQuery,
)
from nanobot.meeting.trace import RunTraceWriter

CASES = Path("tests/fixtures/meeting/evaluation/lifecycle_cases.json")


def test_prebrief_workflow_generates_sourced_read_only_brief(tmp_path: Path) -> None:
    store = MeetingMemoryStore(tmp_path)
    store.persist_entity_memory(
        EntityMemory(
            entity_type=MemoryEntityType.PROJECT,
            entity_id="alpha",
            name="Alpha",
            summary="上次决定先灰度上线。",
            source_meeting_ids=["meeting-1"],
            source_segment_ids=["seg-0001"],
        )
    )

    brief = PreBriefWorkflow(tmp_path, "fake").generate(
        PreBriefInput(
            meeting_ref=MeetingRef(type=MeetingRefType.LATEST_ENDED, query="Alpha 项目例会"),
            meeting_type=MeetingType.PROJECT_SYNC,
            project="Alpha",
        )
    )

    assert brief.run_id
    assert brief.goal
    assert brief.trace_path
    assert any(section.title == "未关闭待办" for section in brief.sections)
    assert not (tmp_path / ".lark_meeting_agent" / "audit.jsonl").exists()


def test_live_workflow_ingests_events_and_answers_with_sources(tmp_path: Path) -> None:
    workflow = LiveMeetingWorkflow(tmp_path)
    state = workflow.start("live-1", "项目例会")
    state = workflow.ingest(
        LiveMeetingEvent(
            event_id="event-1",
            live_run_id=state.live_run_id,
            meeting_id="live-1",
            kind=LiveEventKind.TRANSCRIPT_DELTA,
            text="Alice 决定先灰度上线。",
            speaker_name="Alice",
            timestamp="00:01",
        )
    )
    state = workflow.ingest(
        LiveMeetingEvent(
            event_id="event-2",
            live_run_id=state.live_run_id,
            meeting_id="live-1",
            kind=LiveEventKind.TRANSCRIPT_DELTA,
            text="Bob 负责补充风险清单。",
            speaker_name="Bob",
            timestamp="00:02",
        )
    )

    answer = workflow.qa(state.live_run_id, "目前有哪些结论和待办？")

    assert state.decision_candidates
    assert state.action_candidates
    assert answer.sufficient is True
    assert answer.sources
    assert answer.sources[0].speaker_name
    assert answer.sources[0].timestamp


def test_retrieval_engine_returns_sources_and_insufficient_fallback(tmp_path: Path) -> None:
    store = MeetingMemoryStore(tmp_path)
    store._append(
        "decisions.jsonl",
        {
            "decision_id": "d1",
            "text": "决定 Alpha 项目先灰度上线",
            "evidence_refs": [
                EvidenceRef(
                    evidence_id="e1",
                    meeting_id="m1",
                    segment_id="seg-0001",
                    quote="决定 Alpha 项目先灰度上线",
                ).model_dump(mode="json")
            ],
        },
    )

    engine = MeetingRetrievalEngine(store)
    result = engine.retrieve(RetrievalQuery(question="Alpha 项目决定了什么？", project="Alpha"))
    missing = engine.answer("完全不存在的事项")

    assert result.sufficient is True
    assert result.items[0].source.meeting_id == "m1"
    assert missing.sufficient is False


def test_run_trace_writer_redacts_secrets(tmp_path: Path) -> None:
    writer = RunTraceWriter(tmp_path, "run-1", "test")
    writer.add("tool", "Authorization: Bearer sk-secret", {"url": "https://x.example/?token=abc", "cookie": "cookie=session"})
    path = writer.save()

    data = path.read_text()
    assert "sk-secret" not in data
    assert "token=abc" not in data
    assert "[REDACTED]" in data


def test_lifecycle_evaluator_computes_resume_profile_metrics(tmp_path: Path) -> None:
    report = LifecycleEvaluator(tmp_path).evaluate_file(CASES, tmp_path / "report.json")

    assert report.passed is True
    assert report.profile == "deterministic-regression"
    assert report.metrics.action_precision >= 0.9
    assert report.metrics.action_recall >= 0.85
    assert report.metrics.evidence_coverage == 1.0
    assert len(report.case_results) >= 30
    assert (tmp_path / "report.json").exists()


@pytest.mark.asyncio
async def test_lark_meeting_tool_routes_lifecycle_actions(tmp_path: Path) -> None:
    tool = LarkMeetingTool(workspace=tmp_path)

    prebrief = json.loads(
        await tool.execute(
            action="prebrief",
            meeting_ref_type="latest_ended",
            query="Alpha 项目例会",
            meeting_type="project_sync",
            project="Alpha",
        )
    )
    live_state = json.loads(
        await tool.execute(
            action="live_ingest",
            meeting_ref_value="live-tool-1",
            event_text="Alice 决定先灰度上线。",
            speaker="Alice",
            timestamp="00:01",
        )
    )
    live_answer = json.loads(await tool.execute(action="live_qa", live_run_id=live_state["live_run_id"], question="有什么结论？"))
    report = json.loads(await tool.execute(action="evaluate", cases_file=str(CASES), output_file=str(tmp_path / "eval.json")))

    assert prebrief["sections"]
    assert live_answer["sources"]
    assert report["passed"] is True
    assert (tmp_path / "eval.json").exists()


@pytest.mark.asyncio
async def test_lark_meeting_tool_routes_live_lark_listener_actions(tmp_path: Path) -> None:
    tool = LarkMeetingTool(workspace=tmp_path)

    session = json.loads(
        await tool.execute(
            action="live_join",
            provider_mode="fake",
            meeting_number="123456789",
            approve_visible_join=True,
            sender_id="ou_live",
            live_approvers=["ou_live"],
        )
    )
    poll = json.loads(
        await tool.execute(
            action="live_poll",
            provider_mode="fake",
            meeting_ref_value=session["meeting_id"],
            live_run_id=session["live_run_id"],
        )
    )
    leave = json.loads(
        await tool.execute(
            action="live_leave",
            provider_mode="fake",
            meeting_ref_value=session["meeting_id"],
            approve_visible_leave=True,
            sender_id="ou_live",
            live_approvers=["ou_live"],
        )
    )

    assert session["meeting_id"] == "live-meeting-1"
    assert poll["state"]["transcript_segments"]
    assert leave["status"] == "left"
