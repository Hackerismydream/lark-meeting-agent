from __future__ import annotations

import argparse
import json
from pathlib import Path

from nanobot.meeting_data.fixture_store import load_fixtures


def main() -> int:
    parser = argparse.ArgumentParser(description="Run source-grounded QA demo over processed fixtures.")
    parser.add_argument("--fixtures", default="data/processed/meeting_fixtures")
    parser.add_argument("--question", default="What evidence supports the meeting summary?")
    parser.add_argument("--out", default="runs/meeting_eval/feishu_qa_demo.json")
    args = parser.parse_args()
    fixtures = load_fixtures(args.fixtures)
    sources = []
    for fixture in fixtures[:10]:
        for turn in fixture.transcript_turns[:2]:
            sources.append(
                {
                    "fixture_id": fixture.fixture_id,
                    "dataset": fixture.dataset.value,
                    "turn_id": turn.turn_id,
                    "speaker": turn.speaker,
                    "text": turn.text,
                    "provenance": fixture.provenance.model_dump(mode="json"),
                }
            )
    answer = {
        "question": args.question,
        "answer": "insufficient evidence" if not sources else "Found source-backed fixture evidence.",
        "sources": sources,
    }
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(answer, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote QA demo evidence to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
