from __future__ import annotations

from pathlib import Path

import pytest

from nanobot.meeting.live_lark import LiveLarkMeetingWorkflow
from nanobot.meeting.simulator import LiveMeetingSimulator, load_scenarios

SCENARIOS = Path("tests/fixtures/meeting/scenarios")


def test_loads_all_v1_scenarios() -> None:
    scenarios = load_scenarios(SCENARIOS)

    assert len(scenarios) == 8
    assert {scenario.meeting_type for scenario in scenarios} >= {
        "customer_poc_review",
        "project_weekly",
        "requirement_review",
        "tech_review",
        "incident_review",
        "one_on_one",
        "sales_cs_followup",
        "long_project_retrospective",
    }
    for scenario in scenarios:
        assert scenario.participants
        assert scenario.agenda
        assert scenario.timeline
        assert scenario.expected.qa_cases
        assert scenario.expected.safety_cases


def test_simulator_emits_lark_like_pages_with_tokens() -> None:
    simulator = LiveMeetingSimulator.from_dir(SCENARIOS / "project_weekly")

    first = simulator.page(page_size=3)
    second = simulator.page(page_size=3, page_token=first.next_page_token)

    assert first.has_more is True
    assert first.next_page_token
    assert second.events
    assert all("event_type" in event for event in first.events)


def test_simulator_can_emit_duplicate_malformed_and_out_of_order_events() -> None:
    simulator = LiveMeetingSimulator.from_dir(SCENARIOS / "tech_review")
    page = simulator.page(page_size=50)

    event_ids = [event.get("event_id") for event in page.events if event.get("event_id")]

    assert len(event_ids) != len(set(event_ids))
    assert any(event.get("event_type") == "malformed_missing_text" for event in page.events)
    assert any(event.get("tags") and "out_of_order" in event["tags"] for event in page.events)


def test_live_session_time_can_be_frozen_for_deterministic_reports(tmp_path: Path) -> None:
    freezegun = pytest.importorskip("freezegun", reason="Freezegun time tests require the dev extra")

    with freezegun.freeze_time("2026-06-10T10:00:00Z"):
        session = LiveLarkMeetingWorkflow(tmp_path, "fake").start_local_session(meeting_id="time-freeze")

    assert session.joined_at.startswith("2026-06-10T10:00:00")
