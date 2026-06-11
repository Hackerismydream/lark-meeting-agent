from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from nanobot.meeting.errors import ToolExecutionError
from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.production import MeetingAgentAccessPolicy, MeetingBotContext, ProductionMeetingBot
from nanobot.meeting.repository import SQLiteMeetingRepository
from nanobot.meeting.schemas import ExecutionStatus, RunStatus
from nanobot.meeting.workflow import PostMeetingWorkflow


def _policy() -> MeetingAgentAccessPolicy:
    return MeetingAgentAccessPolicy(
        allowed_users={"ou_allowed"},
        admin_users={"ou_admin"},
        write_approvers={"ou_approver"},
    )


def test_restart_can_status_and_approve_existing_run_from_sqlite(tmp_path: Path) -> None:
    repository = SQLiteMeetingRepository(tmp_path / "meeting.db")
    bot = ProductionMeetingBot(tmp_path, _policy(), repository=repository)
    process_reply = bot.handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting process Alpha")
    operations = repository.list_write_operations(process_reply.run_id or "")

    shutil.rmtree(tmp_path / ".lark_meeting_agent")
    restarted = ProductionMeetingBot(tmp_path, _policy(), repository=repository)
    status_reply = restarted.handle_message(MeetingBotContext(sender_id="ou_allowed"), f"/meeting status {process_reply.run_id}")
    approve_reply = restarted.handle_message(
        MeetingBotContext(sender_id="ou_approver"),
        f"/meeting approve {process_reply.run_id} " + " ".join(operation.operation_id for operation in operations),
    )

    persisted = repository.load_run(process_reply.run_id or "")
    assert status_reply.status == "ok"
    assert approve_reply.status == "ok"
    assert persisted.status == RunStatus.COMPLETED
    assert all(operation.execution_status == ExecutionStatus.COMPLETED for operation in persisted.write_plan.operations)


def test_duplicate_approve_after_restart_does_not_duplicate_completed_write_rows(tmp_path: Path) -> None:
    repository = SQLiteMeetingRepository(tmp_path / "meeting.db")
    bot = ProductionMeetingBot(tmp_path, _policy(), repository=repository)
    process_reply = bot.handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting process Alpha")
    operation_ids = [operation.operation_id for operation in repository.list_write_operations(process_reply.run_id or "")]

    bot.handle_message(MeetingBotContext(sender_id="ou_approver"), f"/meeting approve {process_reply.run_id} " + " ".join(operation_ids))
    second = ProductionMeetingBot(tmp_path, _policy(), repository=repository)
    second.handle_message(MeetingBotContext(sender_id="ou_approver"), f"/meeting approve {process_reply.run_id} " + " ".join(operation_ids))

    operations = repository.list_write_operations(process_reply.run_id or "")
    assert len(operations) == len(operation_ids)
    assert all(operation.execution_status == ExecutionStatus.COMPLETED for operation in operations)


def test_failed_write_marks_run_needs_reconciliation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workflow = PostMeetingWorkflow(tmp_path, provider_mode="fake", analyzer_mode="fake")
    process = workflow.process_transcript_file(
        Path("tests/fixtures/meeting/transcripts/sample_project_sync.txt"),
        create_doc=True,
        create_tasks=True,
        dry_run=True,
    )
    run = workflow.memory.load_run_snapshot(process.run_id)

    adapter = LarkToolAdapter.fake(tmp_path)
    original_execute = adapter.execute

    def execute_with_failure(operation: str, payload: dict, **kwargs):
        if operation == "task.create":
            raise ToolExecutionError("simulated task failure")
        return original_execute(operation, payload, **kwargs)

    adapter.execute = execute_with_failure
    monkeypatch.setattr(workflow, "_adapter", lambda mode: adapter)

    approved = workflow.approve_run(run, [operation.operation_id for operation in run.write_plan.operations])

    statuses = [operation.execution_status for operation in approved.write_plan.operations]
    assert ExecutionStatus.COMPLETED in statuses
    assert ExecutionStatus.FAILED in statuses
    assert approved.status == RunStatus.PARTIAL_SUCCESS
