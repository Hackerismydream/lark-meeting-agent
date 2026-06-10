from __future__ import annotations

from pathlib import Path

import pytest

from nanobot.agent.tools.lark_meeting import LarkMeetingTool
from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.errors import ApprovalProviderMismatchError
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


def test_process_snapshot_records_provider_and_analyzer_modes(tmp_path: Path) -> None:
    workflow = PostMeetingWorkflow(workspace=tmp_path, provider_mode="cli", analyzer_mode="fake")
    result = workflow.process_transcript_file(FIXTURE, create_doc=True, create_tasks=False, dry_run=True)

    run = MeetingMemoryStore(tmp_path).load_run_snapshot(result.run_id)

    assert run.provider_mode == "cli"
    assert run.analyzer_mode == "fake"
    assert run.write_plan_created_at
    assert run.write_plan is not None
    assert all(op.idempotency_key for op in run.write_plan.operations)


def test_approve_rejects_provider_mismatch_without_override(tmp_path: Path) -> None:
    workflow = PostMeetingWorkflow(workspace=tmp_path, provider_mode="fake", analyzer_mode="fake")
    result = workflow.process_transcript_file(FIXTURE, create_doc=True, create_tasks=False, dry_run=True)
    operation_id = result.write_plan.operations[0].operation_id

    with pytest.raises(ApprovalProviderMismatchError):
        workflow.approve(result.run_id, [operation_id], provider_mode="cli")


def test_repeated_approve_does_not_execute_completed_operation_again(tmp_path: Path) -> None:
    workflow = PostMeetingWorkflow(workspace=tmp_path, provider_mode="fake", analyzer_mode="fake")
    result = workflow.process_transcript_file(FIXTURE, create_doc=True, create_tasks=False, dry_run=True)
    operation_id = result.write_plan.operations[0].operation_id

    first = workflow.approve(result.run_id, [operation_id])
    second = workflow.approve(result.run_id, [operation_id])

    first_op = first.write_plan.operations[0]
    second_op = second.write_plan.operations[0]
    assert first_op.execution_status == ExecutionStatus.COMPLETED
    assert second_op.execution_status == ExecutionStatus.COMPLETED
    assert first_op.result == second_op.result


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
