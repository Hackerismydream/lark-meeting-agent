from __future__ import annotations

from pathlib import Path

import pytest

from nanobot.meeting.errors import ApprovalRequiredError, ToolExecutionError
from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.live_lark import LiveLarkMeetingWorkflow
from nanobot.meeting.production import MeetingAgentAccessPolicy, MeetingBotContext, ProductionMeetingBot
from nanobot.meeting.schemas import ApprovalStatus


def test_live_join_rejects_invalid_meeting_number_before_provider_call(tmp_path: Path) -> None:
    workflow = LiveLarkMeetingWorkflow(tmp_path, provider_mode="fake")

    with pytest.raises(ToolExecutionError):
        workflow.join(
            meeting_number="12345abc",
            dry_run=False,
            approval_status=ApprovalStatus.APPROVED,
        )

    assert workflow.adapter.audit_events == []


def test_meeting_password_fields_are_redacted_from_audit(tmp_path: Path) -> None:
    adapter = LarkToolAdapter.fake(tmp_path)

    adapter.execute(
        "vc.meeting.join",
        {"meeting_number": "123456789", "password": "secret-pass", "passcode": "secret-code", "meeting_password": "secret-mp"},
        dry_run=True,
    )
    audit = adapter.audit_events[-1].model_dump_json()

    assert "secret-pass" not in audit
    assert "secret-code" not in audit
    assert "secret-mp" not in audit
    assert "[REDACTED]" in audit


def test_chat_participant_and_share_events_are_tracked_in_live_state(tmp_path: Path) -> None:
    workflow = LiveLarkMeetingWorkflow(tmp_path, provider_mode="fake")
    session = workflow.start_local_session(meeting_id="live-hardening")
    poll = workflow.ingest_raw_events(
        session,
        {
            "events": [
                {"event_id": "p1", "event_type": "participant_joined", "participant": {"name": "Alice"}, "timestamp": "00:00"},
                {"event_id": "s1", "event_type": "magic_share_started", "speaker": {"name": "Alice"}, "text": "开始共享方案文档", "timestamp": "00:01"},
                {"event_id": "c1", "event_type": "chat_received", "sender": {"name": "Bob"}, "message": {"text": "Bob 负责补充风险清单。"}, "segment_id": "chat-1", "timestamp": "00:02"},
            ],
            "has_more": True,
            "page_token": "token-2",
        },
    )
    answer = workflow.qa(session.live_run_id, "目前有哪些待办？")

    assert poll.state.page_token == "token-2"
    assert poll.state.has_more is True
    assert any(event["kind"] == "participant_join" for event in poll.state.event_timeline)
    assert any("共享方案文档" in str(event.get("text")) for event in poll.state.event_timeline)
    assert answer.sources[0].segment_id == "chat-1"


def test_repeated_poll_deduplicates_event_ids_and_reuses_page_token(tmp_path: Path) -> None:
    workflow = LiveLarkMeetingWorkflow(tmp_path, provider_mode="fake")
    session = workflow.start_local_session(meeting_id="live-dedupe")
    raw = {
        "events": [
            {"event_id": "e1", "event_type": "transcript_received", "speaker": {"name": "Alice"}, "transcript": {"text": "Alice 决定继续灰度。"}, "segment_id": "seg-1"},
        ],
        "next_page_token": "token-next",
    }

    first = workflow.ingest_raw_events(session, raw)
    second = workflow.ingest_raw_events(first.session, raw)

    assert len(first.state.transcript_segments) == 1
    assert len(second.state.transcript_segments) == 1
    assert second.session.page_token == "token-next"
    assert second.state.page_token == "token-next"


def test_live_join_and_leave_without_approval_are_rejected(tmp_path: Path) -> None:
    workflow = LiveLarkMeetingWorkflow(tmp_path, provider_mode="fake")

    with pytest.raises(ApprovalRequiredError):
        workflow.join(meeting_number="123456789", dry_run=False)

    with pytest.raises(ApprovalRequiredError):
        workflow.leave("live-meeting-1", dry_run=False)


def test_production_bot_does_not_route_live_join_for_untrusted_sender(tmp_path: Path) -> None:
    bot = ProductionMeetingBot(tmp_path, MeetingAgentAccessPolicy(allowed_users={"ou_allowed"}))

    reply = bot.handle_message(MeetingBotContext(sender_id="ou_unknown"), "/meeting live-join 123456789")

    assert reply.status == "denied"
