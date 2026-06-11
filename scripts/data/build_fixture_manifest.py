from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from nanobot.meeting_data.fixture_store import load_fixtures
from nanobot.meeting_data.sampling import write_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a manifest for processed meeting fixtures.")
    parser.add_argument("--fixtures", default="data/processed/meeting_fixtures")
    parser.add_argument("--out", default="data/manifests/tiny30_manifest.jsonl")
    parser.add_argument("--lock", default="data/manifests/fixture_lock.json")
    parser.add_argument("--seed", type=int, default=20260611)
    args = parser.parse_args()
    rows = []
    fixtures = load_fixtures(Path(args.fixtures))
    for fixture in fixtures:
        rows.append(
            {
                "fixture_id": fixture.fixture_id,
                "dataset": fixture.dataset.value,
                "source_id": fixture.provenance.source_id,
                "source_split": fixture.provenance.source_split or "unknown",
                "source_domain": fixture.provenance.source_domain or "unknown",
                "source_path": fixture.provenance.source_path or "",
                "selected_reason": "processed fixture manifest",
                "license": fixture.provenance.license or "",
                "processed_path": str(Path(args.fixtures)),
                "raw_available": fixture.provenance.raw_available,
            }
        )
    write_manifest(rows, args.out)
    lock = {
        "seed": args.seed,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fixture_count": len(fixtures),
        "datasets": {},
    }
    for fixture in fixtures:
        dataset = fixture.dataset.value
        lock["datasets"].setdefault(dataset, {"count": 0, "fixture_ids": []})
        lock["datasets"][dataset]["count"] += 1
        lock["datasets"][dataset]["fixture_ids"].append(fixture.fixture_id)
    lock_path = Path(args.lock)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {len(rows)} manifest rows to {args.out}")
    print(f"wrote fixture lock to {args.lock}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
