from __future__ import annotations

import json
import wave
from pathlib import Path

from nanobot.meeting.input_provider import (
    LocalAudioFileProvider,
    LocalTranscriptProvider,
    MeetingInputSourceError,
    ProviderCapability,
    MeetingInputProviderConfig,
    ProviderStatus,
)
from nanobot.meeting.schemas import LiveEventKind


def test_local_transcript_provider_replays_text_as_canonical_events(tmp_path: Path) -> None:
    transcript = tmp_path / "meeting.txt"
    transcript.write_text("[00:01] Alice: 决定先做本地监听。\n[00:02] Bob: 我负责补充测试。", encoding="utf-8")
    provider = LocalTranscriptProvider(tmp_path)

    session = provider.start(
        MeetingInputProviderConfig(
            provider_name="local_transcript",
            meeting_id="local-meeting-1",
            source_path="meeting.txt",
            live_run_id="live-1",
        )
    )
    batch = provider.poll(session)
    second = provider.poll(batch.session)

    assert batch.status == ProviderStatus.EXHAUSTED
    assert ProviderCapability.TRANSCRIPT_EVENTS in session.capabilities
    assert [event.kind for event in batch.events] == [LiveEventKind.TRANSCRIPT_DELTA, LiveEventKind.TRANSCRIPT_DELTA]
    assert [event.segment_id for event in batch.events] == ["seg-0001", "seg-0002"]
    assert batch.transcript_segments[0].speaker_name == "Alice"
    assert batch.events[1].text == "我负责补充测试。"
    assert second.events == []


def test_local_transcript_provider_keeps_json_segment_ids_stable(tmp_path: Path) -> None:
    transcript = tmp_path / "meeting.json"
    transcript.write_text(
        json.dumps(
            [
                {"segment_id": "s-custom-1", "speaker": "Alice", "timestamp": "00:01", "text": "确认方案。"},
                {"segment_id": "s-custom-2", "speaker": "Bob", "timestamp": "00:02", "text": "跟进权限。"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    provider = LocalTranscriptProvider(tmp_path)
    config = MeetingInputProviderConfig(
        provider_name="local_transcript",
        meeting_id="local-meeting-json",
        source_path="meeting.json",
        live_run_id="live-json",
    )

    first = provider.poll(provider.start(config))
    second = provider.poll(provider.start(config))

    assert [event.segment_id for event in first.events] == ["s-custom-1", "s-custom-2"]
    assert [event.segment_id for event in first.events] == [event.segment_id for event in second.events]


def test_local_audio_file_provider_uses_transcript_sidecar(tmp_path: Path) -> None:
    audio = tmp_path / "meeting.wav"
    _write_wav(audio)
    transcript = tmp_path / "meeting.txt"
    transcript.write_text("Alice: 决定继续推进。", encoding="utf-8")
    provider = LocalAudioFileProvider(tmp_path)

    session = provider.start(
        MeetingInputProviderConfig(
            provider_name="local_audio_file",
            meeting_id="audio-meeting-1",
            source_path="meeting.wav",
            transcript_path="meeting.txt",
            live_run_id="audio-live-1",
        )
    )
    batch = provider.poll(session)

    assert session.metadata["audio_file_type"] == "wav"
    assert session.metadata["sample_rate_hz"] == "8000"
    assert batch.events[0].kind == LiveEventKind.TRANSCRIPT_DELTA
    assert batch.events[0].text == "决定继续推进。"
    assert batch.transcript_segments[0].speaker_name == "Alice"


def test_local_audio_file_provider_without_sidecar_emits_marker_only(tmp_path: Path) -> None:
    audio = tmp_path / "meeting.mp3"
    audio.write_bytes(b"not a real mp3, but a local selected file")
    provider = LocalAudioFileProvider(tmp_path)

    session = provider.start(
        MeetingInputProviderConfig(
            provider_name="local_audio_file",
            meeting_id="audio-meeting-2",
            source_path="meeting.mp3",
            live_run_id="audio-live-2",
        )
    )
    batch = provider.poll(session)

    assert batch.transcript_segments == []
    assert len(batch.events) == 1
    assert batch.events[0].kind == LiveEventKind.MARKER
    assert "no transcript sidecar" in (batch.events[0].text or "")


def test_local_audio_file_provider_rejects_unsupported_file_type(tmp_path: Path) -> None:
    source = tmp_path / "meeting.mov"
    source.write_bytes(b"video")
    provider = LocalAudioFileProvider(tmp_path)

    try:
        provider.start(
            MeetingInputProviderConfig(
                provider_name="local_audio_file",
                meeting_id="audio-meeting-3",
                source_path="meeting.mov",
            )
        )
    except MeetingInputSourceError as exc:
        assert "unsupported audio file type" in str(exc)
    else:
        raise AssertionError("unsupported audio file was accepted")


def test_local_transcript_provider_append_mode_emits_only_new_lines(tmp_path: Path) -> None:
    transcript = tmp_path / "append.txt"
    transcript.write_text("", encoding="utf-8")
    provider = LocalTranscriptProvider(tmp_path)
    session = provider.start(
        MeetingInputProviderConfig(
            provider_name="local_transcript",
            meeting_id="append-meeting",
            source_path="append.txt",
            live_run_id="append-live",
            append_mode=True,
        )
    )

    first = provider.poll(session)
    transcript.write_text("[00:01] Alice: 决定采用本地 transcript live。\n", encoding="utf-8")
    second = provider.poll(first.session)
    third = provider.poll(second.session)
    transcript.write_text(
        "[00:01] Alice: 决定采用本地 transcript live。\n[00:02] Bob: 我负责补充测试。\n",
        encoding="utf-8",
    )
    fourth = provider.poll(third.session)

    assert ProviderCapability.APPEND_POLLING in session.capabilities
    assert first.status == ProviderStatus.RUNNING
    assert first.events == []
    assert [event.segment_id for event in second.events] == ["seg-0001"]
    assert third.events == []
    assert [event.segment_id for event in fourth.events] == ["seg-0002"]
    assert fourth.status == ProviderStatus.RUNNING


def test_local_transcript_provider_stop_prevents_more_events(tmp_path: Path) -> None:
    transcript = tmp_path / "append.txt"
    transcript.write_text("[00:01] Alice: 决定先做。", encoding="utf-8")
    provider = LocalTranscriptProvider(tmp_path)
    session = provider.start(
        MeetingInputProviderConfig(
            provider_name="local_transcript",
            meeting_id="stop-meeting",
            source_path="append.txt",
            append_mode=True,
        )
    )
    provider.stop(session)
    transcript.write_text("[00:01] Alice: 决定先做。\n[00:02] Bob: 我负责补充。", encoding="utf-8")

    batch = provider.poll(session)

    assert batch.status == ProviderStatus.STOPPED
    assert batch.events == []


def _write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 8000)
