from __future__ import annotations

import pytest

from nanobot.meeting_data.fixture_store import read_jsonl
from nanobot.meeting_data.sampling import deterministic_sample, stratified_sample, write_manifest


def test_deterministic_sample_is_repeatable() -> None:
    items = list(range(20))

    assert deterministic_sample(items, 5) == deterministic_sample(items, 5)


def test_stratified_sample_respects_counts() -> None:
    items = ["a1", "a2", "b1", "b2", "b3"]

    selected = stratified_sample(items, lambda item: item[0], {"a": 1, "b": 2})

    assert len([item for item in selected if item.startswith("a")]) == 1
    assert len([item for item in selected if item.startswith("b")]) == 2


def test_write_manifest_validates_required_fields(tmp_path) -> None:
    with pytest.raises(ValueError, match="missing fields"):
        write_manifest([{"fixture_id": "x"}], tmp_path / "bad.jsonl")


def test_write_manifest_round_trip(tmp_path) -> None:
    record = {
        "fixture_id": "fixture-1",
        "dataset": "qmsum",
        "source_id": "source-1",
        "source_split": "test",
        "source_domain": "Product",
        "source_path": "raw.json",
        "selected_reason": "test",
        "license": "research",
        "processed_path": "fixture.json",
        "raw_available": True,
    }
    path = write_manifest([record], tmp_path / "manifest.jsonl")

    assert read_jsonl(path) == [record]
