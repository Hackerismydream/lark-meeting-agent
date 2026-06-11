from __future__ import annotations

from pathlib import Path

import pytest

from nanobot.meeting_data.adapters.vcsum import DOWNLOAD_INSTRUCTIONS, load_records, prepare_tiny10, record_to_fixture


RAW = Path("tests/fixtures/meeting_data/raw_samples/vcsum")


def test_vcsum_adapter_parses_toy_sample() -> None:
    fixture = record_to_fixture(load_records(RAW)[0])

    assert fixture.dataset.value == "vcsum"
    assert fixture.meta.language == "zh"
    assert fixture.topic_segments
    assert fixture.expected.salient_turn_ids


def test_vcsum_prepare_writes_fixture_and_manifest(tmp_path) -> None:
    fixtures = prepare_tiny10(RAW, tmp_path / "out", tmp_path / "manifest.jsonl")

    assert len(fixtures) == 1
    assert (tmp_path / "out" / f"{fixtures[0].fixture_id}.json").exists()


def test_vcsum_missing_raw_has_clear_instructions(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="VCSum raw data is missing"):
        load_records(tmp_path / "missing")
    assert "hahahawu/VCSum" in DOWNLOAD_INSTRUCTIONS
