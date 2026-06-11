from __future__ import annotations

import argparse
import json

from nanobot.meeting_eval.runner import run_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="Run meeting-data evaluation suite.")
    parser.add_argument("--suite", default="tiny30")
    parser.add_argument("--mode", choices=["mock_smoke", "agent"], default="mock_smoke")
    parser.add_argument("--fixtures", default="data/processed/meeting_fixtures")
    parser.add_argument("--out", default="runs/meeting_eval")
    args = parser.parse_args()
    result = run_suite(args.suite, args.fixtures, args.out, mode=args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
