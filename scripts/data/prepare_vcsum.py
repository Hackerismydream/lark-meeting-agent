from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nanobot.meeting_data.adapters.vcsum import DOWNLOAD_INSTRUCTIONS, prepare_tiny10


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare VCSum tiny10 fixtures.")
    parser.add_argument("--raw", default="data/raw/vcsum")
    parser.add_argument("--out", default="data/processed/meeting_fixtures/vcsum/tiny10")
    parser.add_argument("--manifest", default="data/manifests/vcsum_tiny10_manifest.jsonl")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260611)
    args = parser.parse_args()
    try:
        fixtures = prepare_tiny10(Path(args.raw), Path(args.out), Path(args.manifest), limit=args.limit, seed=args.seed)
    except FileNotFoundError:
        print(DOWNLOAD_INSTRUCTIONS, file=sys.stderr)
        return 2
    print(f"prepared {len(fixtures)} VCSum fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
