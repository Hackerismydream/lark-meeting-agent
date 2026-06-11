from __future__ import annotations

from nanobot.meeting_data.feishu_wrapper import fixture_to_feishu_context
from nanobot.meeting_data.fixture_store import read_jsonl
from nanobot.meeting_data.lark_mock import MockLarkTools
from tests.meeting_data.test_fixture_schema import valid_fixture


def test_mock_lark_tools_write_local_artifacts_and_trace(tmp_path) -> None:
    fixture = valid_fixture()
    context = fixture_to_feishu_context(fixture)
    tools = MockLarkTools(tmp_path, run_id="run-1")

    tools.get_calendar_event(context)
    tools.get_agenda_doc(context)
    tools.stream_transcript(context)
    tools.create_minutes_doc(fixture)
    tools.create_action_items(fixture)
    tools.create_decision_log(fixture)
    tools.send_follow_up_message(fixture)
    tools.write_report({"ok": True})

    assert (tmp_path / "run-1" / "artifacts" / "minutes.md").exists()
    assert (tmp_path / "run-1" / "artifacts" / "action_items.json").exists()
    event_types = {row["event_type"] for row in read_jsonl(tmp_path / "run-1" / "trace.jsonl")}
    assert {"tool_call_started", "tool_call_succeeded", "artifact_created", "eval_observation"} <= event_types
