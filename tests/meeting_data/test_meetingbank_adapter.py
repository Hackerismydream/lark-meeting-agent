from __future__ import annotations

from pathlib import Path

import pytest

from nanobot.meeting_data.adapters.meetingbank import DOWNLOAD_INSTRUCTIONS, load_records, prepare_tiny10, record_to_fixture


RAW = Path("tests/fixtures/meeting_data/raw_samples/meetingbank")


def test_meetingbank_adapter_parses_toy_sample() -> None:
    fixture = record_to_fixture(load_records(RAW)[0])

    assert fixture.dataset.value == "meetingbank"
    assert fixture.transcript_turns
    assert fixture.agenda
    assert fixture.expected.overall_summary


def test_meetingbank_prepare_writes_fixture_and_manifest(tmp_path) -> None:
    fixtures = prepare_tiny10(RAW, tmp_path / "out", tmp_path / "manifest.jsonl")

    assert len(fixtures) == 1
    assert (tmp_path / "out" / f"{fixtures[0].fixture_id}.json").exists()
    assert (tmp_path / "manifest.jsonl").exists()


def test_meetingbank_missing_raw_has_clear_instructions(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="MeetingBank raw data is missing"):
        load_records(tmp_path / "missing")
    assert "zenodo.org" in DOWNLOAD_INSTRUCTIONS
