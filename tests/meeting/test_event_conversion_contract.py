from __future__ import annotations

from pathlib import Path

from nanobot.meeting.live_lark import LiveLarkMeetingWorkflow
from nanobot.meeting.simulator import LiveMeetingSimulator

SCENARIOS = Path("tests/fixtures/meeting/scenarios")


def test_transcript_and_chat_events_become_source_segments(tmp_path: Path) -> None:
    simulator = LiveMeetingSimulator.from_dir(SCENARIOS / "customer_poc_review")
    workflow = LiveLarkMeetingWorkflow(tmp_path, provider_mode="fake")
    session = workflow.start_local_session(meeting_id=simulator.scenario.scenario_id)

    events = workflow.convert_events(simulator.page(page_size=50).model_dump(mode="json"), session=session)
    text_events = [event for event in events if event.text]

    assert any("验收标准" in str(event.text) for event in text_events)
    assert any("安全审计" in str(event.text) for event in text_events)


def test_unknown_and_malformed_events_do_not_crash_conversion(tmp_path: Path) -> None:
    workflow = LiveLarkMeetingWorkflow(tmp_path, provider_mode="fake")
    session = workflow.start_local_session(meeting_id="malformed")

    events = workflow.convert_events(
        {
            "events": [
                {"event_id": "unknown-1", "event_type": "unknown_type", "payload": {"x": 1}},
                {"event_id": "bad-1", "event_type": "transcript_received", "speaker": {"name": "Alice"}},
                "not-a-dict",
            ]
        },
        session=session,
    )

    assert events == []
