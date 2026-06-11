from __future__ import annotations

from nanobot.meeting_data.schemas import TranscriptTurn
from nanobot.meeting_data.streaming import build_transcript_chunks


def test_streaming_is_deterministic_and_preserves_turn_order() -> None:
    turns = [
        TranscriptTurn(turn_id="turn-1", text="a" * 20, start_sec=0, end_sec=5),
        TranscriptTurn(turn_id="turn-2", text="b" * 20, start_sec=6, end_sec=10),
        TranscriptTurn(turn_id="turn-3", text="c" * 20, start_sec=40, end_sec=45),
    ]

    first = build_transcript_chunks(turns, chunk_size_sec=30, max_chars=100)
    second = build_transcript_chunks(turns, chunk_size_sec=30, max_chars=100)

    assert first == second
    assert [turn_id for chunk in first for turn_id in chunk.turn_ids] == ["turn-1", "turn-2", "turn-3"]
    assert all(chunk.end_sec >= chunk.start_sec for chunk in first)
