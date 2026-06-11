from __future__ import annotations

import argparse
import os
from pathlib import Path

from nanobot.meeting.workflow import PostMeetingWorkflow
from nanobot.meeting_data.fixture_store import load_fixture


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run or opt-in sandbox Feishu postmeeting demo.")
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--provider-mode", default="fake", choices=["fake", "cli", "oapi"])
    parser.add_argument("--chat-id", default=os.environ.get("LMA_DEMO_SANDBOX_CHAT_ID"))
    args = parser.parse_args()
    fixture = load_fixture(args.fixture)
    transcript_path = Path("runs/meeting_eval/demo_transcripts") / f"{fixture.fixture_id}.txt"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text("\n".join(turn.text for turn in fixture.transcript_turns), encoding="utf-8")

    real_writes = os.environ.get("LMA_DEMO_ENABLE_REAL_WRITES") == "1"
    if real_writes and not args.chat_id:
        raise SystemExit("LMA_DEMO_ENABLE_REAL_WRITES=1 requires --chat-id or LMA_DEMO_SANDBOX_CHAT_ID")

    workflow = PostMeetingWorkflow(args.workspace, provider_mode=args.provider_mode)
    result = workflow.process_transcript_file(
        transcript_path,
        create_doc=True,
        create_tasks=True,
        send_message=bool(args.chat_id),
        chat_id=args.chat_id,
        dry_run=True,
        provider_mode=args.provider_mode,
        analyzer_mode="fake",
    )
    print(result.model_dump_json(indent=2))
    if real_writes and result.write_plan:
        operation_ids = [operation.operation_id for operation in result.write_plan.operations]
        approved = workflow.approve(result.run_id, operation_ids, provider_mode=args.provider_mode)
        print(approved.model_dump_json(indent=2))
    else:
        print("dry-run only; set LMA_DEMO_ENABLE_REAL_WRITES=1 with sandbox targets for approved writes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
