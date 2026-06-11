"""Read and write canonical meeting fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from nanobot.meeting_data.schemas import MeetingFixture


def save_fixture(fixture: MeetingFixture, path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(fixture.model_dump_json(indent=2), encoding="utf-8")
    return target


def load_fixture(path: Path | str) -> MeetingFixture:
    return MeetingFixture.model_validate_json(Path(path).read_text(encoding="utf-8"))


def load_fixtures(root: Path | str) -> list[MeetingFixture]:
    base = Path(root)
    if base.is_file():
        return [load_fixture(base)]
    fixtures: list[MeetingFixture] = []
    for path in sorted(base.rglob("*.json")):
        fixtures.append(load_fixture(path))
    return fixtures


def write_jsonl(records: Iterable[dict[str, Any]], path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return target


def read_jsonl(path: Path | str) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {source}:{lineno}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row must be an object at {source}:{lineno}")
        rows.append(value)
    return rows


def validate_fixture_dir(root: Path | str) -> list[MeetingFixture]:
    fixtures = load_fixtures(root)
    if not fixtures:
        raise ValueError(f"no fixture JSON files found under {root}")
    return fixtures
