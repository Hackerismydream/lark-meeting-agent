from __future__ import annotations

from pathlib import Path

import pytest

hypothesis = pytest.importorskip("hypothesis", reason="Hypothesis fuzz tests require the dev extra")
given = hypothesis.given
st = hypothesis.strategies

from nanobot.meeting.live_lark import LiveLarkMeetingWorkflow


@given(st.dictionaries(keys=st.text(min_size=0, max_size=20), values=st.one_of(st.none(), st.text(), st.integers(), st.booleans())))
def test_raw_event_conversion_never_crashes_or_executes_tools(tmp_path: Path, raw_event: dict) -> None:
    workflow = LiveLarkMeetingWorkflow(tmp_path, provider_mode="fake")
    session = workflow.start_local_session(meeting_id="fuzz")

    events = workflow.convert_events({"events": [raw_event]}, session=session)

    assert workflow.adapter.audit_events == []
    assert isinstance(events, list)
