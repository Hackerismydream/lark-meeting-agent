from __future__ import annotations

from pathlib import Path

import pytest

from nanobot.agent.tools.lark_meeting import LarkMeetingTool
from nanobot.meeting.production import (
    MeetingAgentAccessPolicy,
    MeetingBotContext,
    ProductionMeetingBot,
    parse_meeting_command,
    validate_production_config,
)
from nanobot.meeting.repository import SQLiteMeetingRepository
from nanobot.meeting.schemas import ApprovalStatus, ExecutionStatus, RunStatus


def _policy() -> MeetingAgentAccessPolicy:
    return MeetingAgentAccessPolicy(
        allowed_users={"ou_allowed"},
        allowed_chat_ids={"oc_allowed"},
        admin_users={"ou_admin"},
        write_approvers={"ou_approver"},
    )


def test_meeting_command_parser_supports_deterministic_commands_and_aliases() -> None:
    process = parse_meeting_command("/meeting process Alpha 项目")
    approve = parse_meeting_command("/meeting approve run-1 op-1,op-2 op-3")
    reject = parse_meeting_command("/meeting reject run-1")
    qa = parse_meeting_command("/meeting qa 上次决定了什么")
    alias = parse_meeting_command("整理最近一场会，先不要写入飞书")

    assert process.action == "process"
    assert process.query == "Alpha 项目"
    assert approve.action == "approve"
    assert approve.operation_ids == ["op-1", "op-2", "op-3"]
    assert reject.action == "reject"
    assert qa.question == "上次决定了什么"
    assert alias.action == "process"
    assert alias.dry_run is True


def test_group_message_without_mention_or_command_is_ignored(tmp_path: Path) -> None:
    bot = ProductionMeetingBot(tmp_path, _policy())

    reply = bot.handle_message(
        MeetingBotContext(sender_id="ou_allowed", chat_id="oc_allowed", chat_type="group", mentioned=False),
        "整理最近一场会",
    )

    assert reply.status == "ignored"


def test_access_policy_denies_unlisted_sender(tmp_path: Path) -> None:
    bot = ProductionMeetingBot(tmp_path, _policy())

    reply = bot.handle_message(MeetingBotContext(sender_id="ou_unknown"), "/meeting status run-1")

    assert reply.status == "denied"
    assert "无权限" in reply.text


def test_production_bot_process_approve_and_reject_protocol(tmp_path: Path) -> None:
    repository = SQLiteMeetingRepository(tmp_path / "meeting.db")
    bot = ProductionMeetingBot(tmp_path, _policy(), repository=repository)

    process_reply = bot.handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting process Alpha")

    assert process_reply.status == RunStatus.APPROVAL_REQUIRED.value
    assert process_reply.run_id
    assert "尚未写入飞书" in process_reply.text
    assert "/meeting approve" in process_reply.text
    assert "/meeting reject" in process_reply.text
    operations = repository.list_write_operations(process_reply.run_id)
    assert operations

    denied = bot.handle_message(
        MeetingBotContext(sender_id="ou_allowed"),
        f"/meeting approve {process_reply.run_id} {operations[0].operation_id}",
    )
    assert denied.status == "denied"

    approve_reply = bot.handle_message(
        MeetingBotContext(sender_id="ou_approver"),
        f"/meeting approve {process_reply.run_id} {operations[0].operation_id}",
    )
    assert approve_reply.status == "ok"
    persisted = repository.list_write_operations(process_reply.run_id)
    assert persisted[0].execution_status == ExecutionStatus.COMPLETED
    assert any(op.execution_status == ExecutionStatus.SKIPPED for op in persisted[1:])

    second_reply = bot.handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting process Beta")
    second_ops = repository.list_write_operations(second_reply.run_id or "")
    reject_reply = bot.handle_message(MeetingBotContext(sender_id="ou_admin"), f"/meeting reject {second_reply.run_id}")
    rejected = repository.load_run(second_reply.run_id or "")

    assert second_ops
    assert reject_reply.status == RunStatus.REJECTED.value
    assert all(op.approval_status == ApprovalStatus.REJECTED for op in rejected.write_plan.operations)


def test_production_config_validation_flags_unsafe_defaults() -> None:
    warnings = validate_production_config(
        {
            "channels": {"feishu": {"allowFrom": ["*"]}},
            "tools": {"exec": {"enable": True}, "restrictToWorkspace": False},
            "meetingAgent": {"writeApprovers": []},
        }
    )

    assert {warning.code for warning in warnings} == {
        "wildcard_allow_from",
        "exec_enabled",
        "workspace_unrestricted",
        "missing_approvers",
    }


@pytest.mark.asyncio
async def test_lark_meeting_tool_routes_bot_message_action(tmp_path: Path) -> None:
    tool = LarkMeetingTool(workspace=tmp_path)

    response = await tool.execute(
        action="bot_message",
        message_text="/meeting process Alpha",
        sender_id="ou_allowed",
        allowed_users=["ou_allowed"],
        write_approvers=["ou_allowed"],
        provider_mode="fake",
        analyzer_mode="fake",
    )

    assert "approval_required" in response
    assert "尚未写入飞书" in response
