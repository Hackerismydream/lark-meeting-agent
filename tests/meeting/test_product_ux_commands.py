from __future__ import annotations

from pathlib import Path

from nanobot.meeting.production import MeetingAgentAccessPolicy, MeetingBotContext, ProductionMeetingBot, parse_meeting_command
from nanobot.meeting.repository import SQLiteMeetingRepository


def _policy() -> MeetingAgentAccessPolicy:
    return MeetingAgentAccessPolicy(
        allowed_users={"ou_allowed"},
        admin_users={"ou_admin"},
        write_approvers={"ou_approver"},
        live_approvers={"ou_live"},
    )


def test_chinese_aliases_parse_to_canonical_commands() -> None:
    assert parse_meeting_command("整理最近一场会").action == "process"
    assert parse_meeting_command("帮我准备 Alpha 项目例会").action == "prebrief"
    assert parse_meeting_command("查询：上次决定了什么").action == "qa"
    assert parse_meeting_command("查看待审批操作").action == "status"
    assert parse_meeting_command("加入会议 123456789").action == "live_join"


def test_ambiguous_confirmation_never_approves(tmp_path: Path) -> None:
    bot = ProductionMeetingBot(tmp_path, _policy(), repository=SQLiteMeetingRepository(tmp_path / "meeting.db"))

    reply = bot.handle_message(MeetingBotContext(sender_id="ou_approver"), "确认")

    assert reply.status == "clarification_required"
    assert "run_id" in reply.text
    assert "operation_id" in reply.text


def test_status_without_run_id_lists_pending_runs(tmp_path: Path) -> None:
    repository = SQLiteMeetingRepository(tmp_path / "meeting.db")
    bot = ProductionMeetingBot(tmp_path, _policy(), repository=repository)
    process = bot.handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting process Alpha")

    status = bot.handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting status")

    assert status.status == "ok"
    assert process.run_id in status.text
    assert "approval_required" in status.text


def test_live_join_requires_explicit_visible_approval(tmp_path: Path) -> None:
    bot = ProductionMeetingBot(tmp_path, _policy(), repository=SQLiteMeetingRepository(tmp_path / "meeting.db"))

    reply = bot.handle_message(MeetingBotContext(sender_id="ou_live"), "/meeting live-join 123456789")

    assert reply.status == "approval_required"
    assert "--approve-visible-join" in reply.text


def test_insufficient_evidence_qa_message_is_explicit(tmp_path: Path) -> None:
    bot = ProductionMeetingBot(tmp_path, _policy(), repository=SQLiteMeetingRepository(tmp_path / "meeting.db"))

    reply = bot.handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting qa 不存在的问题")

    assert reply.status == "insufficient_evidence"
    assert "insufficient evidence" in reply.text
