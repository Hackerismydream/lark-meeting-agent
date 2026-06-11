from __future__ import annotations

import argparse
import json
from pathlib import Path

from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.schemas import MeetingRef, MeetingRefType, MeetingType, PreBriefInput, ProviderMode


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run Feishu prebrief demo.")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--query", default="项目例会")
    parser.add_argument("--provider-mode", default="fake", choices=[mode.value for mode in ProviderMode])
    parser.add_argument("--out", default="runs/meeting_eval/feishu_prebrief_demo.json")
    args = parser.parse_args()
    workflow = PreBriefWorkflow(args.workspace, provider_mode=args.provider_mode)
    brief = workflow.generate(
        PreBriefInput(
            meeting_ref=MeetingRef(type=MeetingRefType.LATEST_ENDED, query=args.query),
            meeting_type=MeetingType.PROJECT_SYNC,
            provider_mode=ProviderMode(args.provider_mode),
        )
    )
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    print(f"wrote dry-run prebrief evidence to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
