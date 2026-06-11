from __future__ import annotations

from nanobot.meeting_data.fixture_store import (
    load_fixture,
    load_fixtures,
    read_jsonl,
    save_fixture,
    validate_fixture_dir,
    write_jsonl,
)
from tests.meeting_data.test_fixture_schema import valid_fixture


def test_save_and_load_fixture(tmp_path) -> None:
    path = save_fixture(valid_fixture(), tmp_path / "fixture.json")

    loaded = load_fixture(path)

    assert loaded.fixture_id == "qmsum-fixture-1"


def test_load_and_validate_fixture_dir(tmp_path) -> None:
    save_fixture(valid_fixture(), tmp_path / "nested" / "fixture.json")

    assert len(load_fixtures(tmp_path)) == 1
    assert validate_fixture_dir(tmp_path)[0].fixture_id == "qmsum-fixture-1"


def test_jsonl_helpers(tmp_path) -> None:
    path = write_jsonl([{"a": 1}, {"b": 2}], tmp_path / "rows.jsonl")

    assert read_jsonl(path) == [{"a": 1}, {"b": 2}]
