from __future__ import annotations

import pytest

from nanobot.meeting.errors import TranscriptNormalizationError
from nanobot.meeting.normalizer import TranscriptNormalizer


def test_normalizes_timestamped_speaker_lines() -> None:
    segments = TranscriptNormalizer().normalize_text(
        meeting_id="meeting-1",
        text="""
        [00:00] 张三: 我们决定本周先灰度上线。
        [00:30] 李四: 我明天确认测试名单。
        """,
    )

    assert [s.segment_id for s in segments] == ["seg-0001", "seg-0002"]
    assert segments[0].speaker_name == "张三"
    assert segments[0].start_time == "00:00"
    assert "灰度上线" in segments[0].text


def test_normalizes_plain_text_as_ordered_segments() -> None:
    segments = TranscriptNormalizer().normalize_text(
        meeting_id="meeting-1",
        text="第一段讨论范围。\n\n第二段决定先灰度上线。",
    )

    assert len(segments) == 2
    assert segments[1].speaker_name is None
    assert segments[1].segment_id == "seg-0002"


def test_rejects_empty_transcript() -> None:
    with pytest.raises(TranscriptNormalizationError):
        TranscriptNormalizer().normalize_text(meeting_id="meeting-1", text="  \n ")
