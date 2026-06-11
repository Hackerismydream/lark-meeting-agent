"""Deterministic fixture sampling helpers."""

from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")


def deterministic_sample(items: list[T], n: int, seed: int = 20260611) -> list[T]:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n >= len(items):
        return list(items)
    indexed = list(enumerate(items))
    rng = random.Random(seed)
    rng.shuffle(indexed)
    selected = sorted(indexed[:n], key=lambda item: item[0])
    return [item for _, item in selected]


def stratified_sample(
    items: list[T],
    key_fn: Callable[[T], str],
    target_counts: dict[str, int],
    seed: int = 20260611,
) -> list[T]:
    by_key: dict[str, list[T]] = {}
    for item in items:
        by_key.setdefault(key_fn(item), []).append(item)
    selected: list[T] = []
    for key, count in target_counts.items():
        selected.extend(deterministic_sample(by_key.get(key, []), count, seed=_seed_for(seed, key)))
    return selected


def write_manifest(records: list[dict[str, Any]], path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for record in records:
            _validate_manifest_record(record)
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return target


def _seed_for(seed: int, key: str) -> int:
    digest = hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()[:8]
    return int(digest, 16)


def _validate_manifest_record(record: dict[str, Any]) -> None:
    required = {
        "fixture_id",
        "dataset",
        "source_id",
        "source_split",
        "source_domain",
        "source_path",
        "selected_reason",
        "license",
        "processed_path",
        "raw_available",
    }
    missing = sorted(required - set(record))
    if missing:
        raise ValueError(f"manifest record missing fields: {missing}")
