from __future__ import annotations

from pathlib import Path

from nanobot.meeting.analyzer import FakeMeetingAnalyzer
from nanobot.meeting.normalizer import TranscriptNormalizer

FIXTURE = Path("tests/fixtures/meeting/transcripts/sample_project_sync.txt")


def test_fake_analyzer_extracts_schema_valid_outputs_with_evidence() -> None:
    segments = TranscriptNormalizer().normalize_text("meeting-1", FIXTURE.read_text())
    minutes = FakeMeetingAnalyzer().analyze(
        meeting_id="meeting-1",
        title="项目例会",
        segments=segments,
    )

    assert minutes.decisions
    assert minutes.action_items
    assert all(d.evidence_refs for d in minutes.decisions)
    assert all(a.evidence_refs for a in minutes.action_items)
    assert minutes.action_items[0].owner in {"张三", "李四", "unassigned", None}
    assert minutes.open_questions[0].text == "是否需要客户确认验收标准。"
