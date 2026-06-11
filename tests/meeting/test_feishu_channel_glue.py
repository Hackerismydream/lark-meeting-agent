from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from nanobot.agent.tools.lark_meeting import LarkMeetingTool
from nanobot.meeting.production import (
    MeetingAgentAccessPolicy,
    ProductionMeetingBot,
    map_feishu_message_event,
)
from nanobot.meeting.repository import SQLiteMeetingRepository


def test_feishu_p2p_message_maps_to_meeting_bot_context() -> None:
    event = {
        "sender": {"sender_id": {"open_id": "ou_sender"}},
        "message": {
            "message_id": "om_msg",
            "chat_id": "oc_dm",
            "chat_type": "p2p",
            "message_type": "text",
            "content": json.dumps({"text": "/meeting process Alpha"}),
        },
    }

    envelope = map_feishu_message_event(event, bot_open_id="ou_bot")

    assert envelope.text == "/meeting process Alpha"
    assert envelope.context.sender_id == "ou_sender"
    assert envelope.context.chat_id == "oc_dm"
    assert envelope.context.chat_type == "dm"
    assert envelope.context.message_id == "om_msg"
    assert envelope.context.mentioned is False


def test_feishu_group_message_detects_bot_mention() -> None:
    event = {
        "sender": {"sender_id": {"open_id": "ou_sender"}},
        "message": {
            "message_id": "om_group",
            "chat_id": "oc_group",
            "chat_type": "group",
            "content": json.dumps({"text": "@MeetingBot /meeting status run-1"}),
            "mentions": [{"id": {"open_id": "ou_bot"}, "name": "MeetingBot"}],
        },
    }

    envelope = map_feishu_message_event(event, bot_open_id="ou_bot")

    assert envelope.context.chat_type == "group"
    assert envelope.context.mentioned is True
    assert envelope.context.message_id == "om_group"
    assert envelope.text.endswith("/meeting status run-1")


def test_production_bot_handles_feishu_event_and_audits_denial(tmp_path: Path) -> None:
    repository = SQLiteMeetingRepository(tmp_path / "meeting.db")
    bot = ProductionMeetingBot(
        tmp_path,
        MeetingAgentAccessPolicy(allowed_users={"ou_allowed"}, allowed_chat_ids={"oc_group"}),
        repository=repository,
    )
    event = {
        "sender": {"sender_id": {"open_id": "ou_unknown"}},
        "message": {
            "message_id": "om_denied",
            "chat_id": "oc_group",
            "chat_type": "group",
            "content": json.dumps({"text": "/meeting status run-1"}),
        },
    }

    reply = bot.handle_feishu_event(event)

    assert reply.status == "denied"
    assert "run-1" not in reply.text
    with sqlite3.connect(tmp_path / "meeting.db") as conn:
        rows = conn.execute("SELECT operation_name, payload_json FROM audit_events").fetchall()
    assert rows
    assert rows[0][0] == "production.policy.denied"
    assert "ou_unknown" in rows[0][1]
    assert "run-1" not in rows[0][1]


@pytest.mark.asyncio
async def test_direct_approve_requires_production_context(tmp_path: Path) -> None:
    tool = LarkMeetingTool(workspace=tmp_path)

    response = await tool.execute(action="approve", run_id="run-1", operation_ids=["op-1"])

    assert response == "Error: production context is required for approve"


@pytest.mark.asyncio
async def test_direct_live_join_requires_live_approver(tmp_path: Path) -> None:
    tool = LarkMeetingTool(workspace=tmp_path)

    denied = await tool.execute(
        action="live_join",
        meeting_number="123456789",
        approve_visible_join=True,
        sender_id="ou_allowed",
        allowed_users=["ou_allowed"],
    )
    allowed = await tool.execute(
        action="live_join",
        provider_mode="fake",
        meeting_number="123456789",
        approve_visible_join=True,
        sender_id="ou_live",
        live_approvers=["ou_live"],
    )

    assert denied == "Error: sender is not allowed to approve live meeting control"
    assert json.loads(allowed)["meeting_id"] == "live-meeting-1"
