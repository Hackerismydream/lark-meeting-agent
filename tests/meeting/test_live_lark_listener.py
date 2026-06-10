from __future__ import annotations

from pathlib import Path

from nanobot.meeting.cli import main
from nanobot.meeting.live_lark import LiveLarkMeetingWorkflow
from nanobot.meeting.schemas import ApprovalStatus


def test_live_lark_workflow_joins_polls_and_ingests_transcript_events(tmp_path: Path) -> None:
    workflow = LiveLarkMeetingWorkflow(tmp_path, provider_mode="fake")

    session = workflow.join(
        meeting_number="123456789",
        dry_run=False,
        approval_status=ApprovalStatus.APPROVED,
    )
    poll = workflow.poll(session.meeting_id, live_run_id=session.live_run_id)
    answer = workflow.qa(session.live_run_id, "目前有哪些结论和待办？")

    assert session.meeting_id == "live-meeting-1"
    assert poll.state.transcript_segments
    assert poll.state.decision_candidates
    assert poll.state.action_candidates
    assert poll.page_token == "page-token-1"
    assert answer.sufficient is True
    assert answer.sources[0].meeting_id == "live-meeting-1"


def test_live_lark_workflow_converts_raw_lark_event_shapes(tmp_path: Path) -> None:
    workflow = LiveLarkMeetingWorkflow(tmp_path, provider_mode="fake")
    session = workflow.start_local_session(meeting_id="live-meeting-2", meeting_number="987654321")

    events = workflow.convert_events(
        {
            "events": [
                {
                    "event_id": "evt-1",
                    "event_type": "transcript_received",
                    "start_time": "00:01",
                    "speaker": {"name": "Alice", "open_id": "ou_alice"},
                    "transcript": {"text": "Alice 决定先灰度上线。"},
                },
                {
                    "id": "evt-2",
                    "type": "chat_received",
                    "timestamp": "00:02",
                    "sender": {"name": "Bob"},
                    "message": {"text": "Bob 负责补充风险清单。"},
                },
            ]
        },
        session=session,
    )

    assert [event.text for event in events] == ["Alice 决定先灰度上线。", "Bob 负责补充风险清单。"]
    assert events[0].speaker_name == "Alice"
    assert events[1].speaker_name == "Bob"


def test_live_lark_cli_entrypoints_use_fake_provider(tmp_path: Path, capsys) -> None:
    assert (
        main(
            [
                "--workspace",
                str(tmp_path),
                "live-join",
                "--meeting-number",
                "123456789",
                "--provider-mode",
                "fake",
                "--approve-visible-join",
            ]
        )
        == 0
    )
    join_output = capsys.readouterr().out
    assert '"meeting_id": "live-meeting-1"' in join_output

    assert (
        main(
            [
                "--workspace",
                str(tmp_path),
                "live-poll",
                "--meeting-id",
                "live-meeting-1",
                "--live-run-id",
                "dry-run-not-used",
                "--provider-mode",
                "fake",
            ]
        )
        == 0
    )
    poll_output = capsys.readouterr().out
    assert '"page_token": "page-token-1"' in poll_output
