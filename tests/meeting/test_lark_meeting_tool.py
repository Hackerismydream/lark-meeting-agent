from __future__ import annotations

import json
from pathlib import Path

import pytest

from nanobot.agent.tools.lark_meeting import LarkMeetingTool

FIXTURE = Path("tests/fixtures/meeting/transcripts/sample_project_sync.txt")


@pytest.mark.asyncio
async def test_lark_meeting_tool_process_status_qa_and_approve(tmp_path: Path) -> None:
    tool = LarkMeetingTool(workspace=tmp_path)

    process_response = await tool.execute(
        action="process",
        meeting_ref_type="transcript_file",
        meeting_ref_value=str(FIXTURE),
        provider_mode="fake",
        analyzer_mode="fake",
        create_doc=True,
        create_tasks=True,
        dry_run=True,
    )
    process_result = json.loads(process_response)
    run_id = process_result["run_id"]
    operation_id = process_result["write_plan"]["operations"][0]["operation_id"]

    status_response = await tool.execute(action="status", run_id=run_id)
    assert json.loads(status_response)["run_id"] == run_id

    qa_response = await tool.execute(action="qa", question="这次会议决定了什么？")
    qa_result = json.loads(qa_response)
    assert qa_result["sources"]
    assert qa_result["sufficient"] is True

    approve_response = await tool.execute(action="approve", run_id=run_id, operation_ids=[operation_id])
    approve_result = json.loads(approve_response)
    completed = [
        op
        for op in approve_result["write_plan"]["operations"]
        if op["execution_status"] == "completed"
    ]
    assert [op["operation_id"] for op in completed] == [operation_id]


@pytest.mark.asyncio
async def test_lark_meeting_tool_validates_required_action_inputs(tmp_path: Path) -> None:
    tool = LarkMeetingTool(workspace=tmp_path)

    assert await tool.execute(action="approve") == "Error: run_id is required for approve"
    assert await tool.execute(action="qa") == "Error: question is required for qa"
    assert await tool.execute(action="status") == "Error: run_id is required for status"
