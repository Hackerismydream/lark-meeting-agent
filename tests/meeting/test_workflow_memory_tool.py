from __future__ import annotations

from pathlib import Path

import pytest

from nanobot.agent.tools.lark_meeting import LarkMeetingTool
from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.schemas import ApprovalStatus, ExecutionStatus
from nanobot.meeting.workflow import PostMeetingWorkflow

FIXTURE = Path("tests/fixtures/meeting/transcripts/sample_project_sync.txt")


def test_post_meeting_workflow_processes_fixture_and_requires_approval(tmp_path: Path) -> None:
    workflow = PostMeetingWorkflow(workspace=tmp_path, provider_mode="fake", analyzer_mode="fake")

    result = workflow.process_transcript_file(
        transcript_file=FIXTURE,
        create_doc=True,
        create_tasks=True,
        send_message=True,
        dry_run=True,
    )

    assert result.status == "approval_required"
    assert result.run_id
    assert result.minutes is not None
    assert result.write_plan is not None
    assert all(op.execution_status == ExecutionStatus.PENDING for op in result.write_plan.operations)
    assert any(op.approval_status == ApprovalStatus.PENDING for op in result.write_plan.operations)


def test_approve_executes_only_selected_operations(tmp_path: Path) -> None:
    workflow = PostMeetingWorkflow(workspace=tmp_path, provider_mode="fake", analyzer_mode="fake")
    result = workflow.process_transcript_file(FIXTURE, create_doc=True, create_tasks=True, dry_run=True)
    assert result.write_plan is not None
    selected = result.write_plan.operations[0].operation_id

    approved = workflow.approve(run_id=result.run_id, operation_ids=[selected])

    executed = [op for op in approved.write_plan.operations if op.execution_status == ExecutionStatus.COMPLETED]
    skipped = [op for op in approved.write_plan.operations if op.execution_status == ExecutionStatus.SKIPPED]
    assert [op.operation_id for op in executed] == [selected]
    assert skipped


def test_meeting_memory_qa_returns_sources_and_insufficient_evidence(tmp_path: Path) -> None:
    workflow = PostMeetingWorkflow(workspace=tmp_path, provider_mode="fake", analyzer_mode="fake")
    workflow.process_transcript_file(FIXTURE, create_doc=False, create_tasks=False, dry_run=True)

    store = MeetingMemoryStore(tmp_path)
    answer = store.qa("这次会议决定了什么？")
    missing = store.qa("完全不存在的预算审批是谁负责？")

    assert answer.sources
    assert "insufficient" not in answer.answer.lower()
    assert missing.sufficient is False


@pytest.mark.asyncio
async def test_lark_meeting_tool_routes_process_action(tmp_path: Path) -> None:
    tool = LarkMeetingTool(workspace=tmp_path)

    response = await tool.execute(
        action="process",
        meeting_ref_type="transcript_file",
        meeting_ref_value=str(FIXTURE),
        provider_mode="fake",
        analyzer_mode="fake",
        create_doc=True,
        create_tasks=True,
        dry_run=True,
    )

    assert "run_id" in response
    assert "approval_required" in response
