from __future__ import annotations

import argparse
from pathlib import Path

from nanobot.meeting_data.fixture_store import load_fixtures
from nanobot.meeting_data.sampling import write_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a manifest for processed meeting fixtures.")
    parser.add_argument("--fixtures", default="data/processed/meeting_fixtures")
    parser.add_argument("--out", default="data/manifests/tiny30_manifest.jsonl")
    args = parser.parse_args()
    rows = []
    for fixture in load_fixtures(Path(args.fixtures)):
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
    print(f"wrote {len(rows)} manifest rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
