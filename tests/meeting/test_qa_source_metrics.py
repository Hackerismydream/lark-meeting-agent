from __future__ import annotations

from nanobot.meeting.metrics import compute_qa_source_accuracy
from nanobot.meeting.schemas import QASource


def test_qa_source_accuracy_requires_expected_segment_ids() -> None:
    score = compute_qa_source_accuracy(
        predicted=[
            QASource(meeting_id="m1", segment_id="seg-1", kind="transcript_segment", text="source"),
            QASource(meeting_id="m1", segment_id="seg-2", kind="transcript_segment", text="source"),
        ],
        expected_segment_ids=["seg-1", "seg-3"],
    )

    assert score == 0.5
