from __future__ import annotations

from pathlib import Path

from nanobot.meeting.live import LiveMeetingWorkflow
from nanobot.meeting.production import MeetingAgentAccessPolicy, MeetingBotContext, ProductionMeetingBot
from nanobot.meeting.repository import SQLiteMeetingRepository
from nanobot.meeting.schemas import LiveEventKind, LiveMeetingEvent


def _bot(tmp_path: Path) -> ProductionMeetingBot:
    return ProductionMeetingBot(
        tmp_path,
        MeetingAgentAccessPolicy(
            allowed_users={"ou_allowed"},
            write_approvers={"ou_approver"},
            live_approvers={"ou_live"},
        ),
        repository=SQLiteMeetingRepository(tmp_path / "meeting.db"),
    )


def test_approval_prompt_snapshot(tmp_path: Path) -> None:
    reply = _bot(tmp_path).handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting process Alpha")

    assert reply.text.splitlines()[:7] == [
        "已生成会议纪要预览，尚未写入飞书。",
        "未审批前不会执行任何飞书写入。",
        "",
        f"Run ID: {reply.run_id}",
        "",
        "摘要:",
        "本周先灰度上线，范围控制在内部用户。",
    ]
    assert "/meeting approve" in reply.text
    assert "/meeting reject" in reply.text


def test_status_snapshot(tmp_path: Path) -> None:
    bot = _bot(tmp_path)
    process = bot.handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting process Alpha")

    status = bot.handle_message(MeetingBotContext(sender_id="ou_allowed"), "查看待审批操作")

    assert status.text == f"待审批 runs:\n- {process.run_id} status=approval_required operations=3"


def test_prebrief_snapshot(tmp_path: Path) -> None:
    reply = _bot(tmp_path).handle_message(MeetingBotContext(sender_id="ou_allowed"), "帮我准备 Alpha 项目例会")

    assert reply.status == "ok"
    assert '"sections"' in reply.text
    assert '"run_id"' in reply.text


def test_live_qa_snapshot(tmp_path: Path) -> None:
    state = LiveMeetingWorkflow(tmp_path).start("meeting-live-1", "Live Demo")
    LiveMeetingWorkflow(tmp_path).ingest(
        LiveMeetingEvent(
            event_id="evt-1",
            live_run_id=state.live_run_id,
            meeting_id="meeting-live-1",
            kind=LiveEventKind.TRANSCRIPT_DELTA,
            text="Alice 决定先灰度上线。",
            speaker_name="Alice",
            timestamp="00:01",
        )
    )

    reply = _bot(tmp_path).handle_message(MeetingBotContext(sender_id="ou_allowed"), f"/meeting live-qa {state.live_run_id} 有什么结论？")

    assert reply.status == "ok"
    assert "Alice 决定先灰度上线" in reply.text
    assert "meeting-live-1" in reply.text


def test_insufficient_evidence_snapshot(tmp_path: Path) -> None:
    reply = _bot(tmp_path).handle_message(MeetingBotContext(sender_id="ou_allowed"), "/meeting qa 谁批准了预算？")

    assert reply.status == "insufficient_evidence"
    assert reply.text == "insufficient evidence: 本地会议知识中没有找到足够证据回答该问题。"
