"""Deterministic transcript chunking for live-meeting simulation."""

from __future__ import annotations

from nanobot.meeting_data.schemas import TranscriptChunk, TranscriptTurn


def build_transcript_chunks(
    turns: list[TranscriptTurn],
    chunk_size_sec: int = 30,
    max_chars: int = 1200,
) -> list[TranscriptChunk]:
    if chunk_size_sec <= 0:
        raise ValueError("chunk_size_sec must be positive")
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    chunks: list[TranscriptChunk] = []
    current: list[TranscriptTurn] = []
    current_start: float | None = None
    current_end: float | None = None
    current_chars = 0

    for index, turn in enumerate(turns):
        start = _start_sec(turn, index)
        end = _end_sec(turn, start)
        would_span = current_start is not None and end - current_start > chunk_size_sec
        would_overflow = current and current_chars + len(turn.text) > max_chars
        if current and (would_span or would_overflow):
            chunks.append(_chunk(len(chunks), current, current_start or 0.0, current_end or current_start or 0.0))
            current = []
            current_start = None
            current_end = None
            current_chars = 0
        if current_start is None:
            current_start = start
        current.append(turn)
        current_end = end
        current_chars += len(turn.text)

    if current:
        chunks.append(_chunk(len(chunks), current, current_start or 0.0, current_end or current_start or 0.0))
    return chunks


def _chunk(index: int, turns: list[TranscriptTurn], start: float, end: float) -> TranscriptChunk:
    return TranscriptChunk(
        chunk_id=f"chunk-{index + 1:04d}",
        turn_ids=[turn.turn_id for turn in turns],
        text="\n".join(_render_turn(turn) for turn in turns),
        start_sec=start,
        end_sec=max(end, start),
    )


def _render_turn(turn: TranscriptTurn) -> str:
    if turn.speaker:
        return f"{turn.speaker}: {turn.text}"
    return turn.text


def _start_sec(turn: TranscriptTurn, index: int) -> float:
    if turn.start_sec is not None:
        return float(turn.start_sec)
    return float(index * 10)


def _end_sec(turn: TranscriptTurn, start: float) -> float:
    if turn.end_sec is not None:
        return float(turn.end_sec)
    return start + 10.0
