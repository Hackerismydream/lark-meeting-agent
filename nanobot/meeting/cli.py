"""Local developer CLI for the meeting MVP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.schemas import MeetingRef, MeetingRefType, ProcessMeetingInput
from nanobot.meeting.workflow import PostMeetingWorkflow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m nanobot.meeting.cli")
    parser.add_argument("--workspace", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    process = sub.add_parser("process")
    process.add_argument("--latest-ended", action="store_true")
    process.add_argument("--query")
    process.add_argument("--transcript-file")
    process.add_argument("--provider-mode", default="fake", choices=["fake", "cli"])
    process.add_argument("--analyzer-mode", default="fake", choices=["fake", "llm"])
    process.add_argument("--create-doc", action="store_true")
    process.add_argument("--create-tasks", action="store_true")
    process.add_argument("--send-message", action="store_true")
    process.add_argument("--chat-id")
    process.add_argument("--dry-run", action="store_true", default=True)

    approve = sub.add_parser("approve")
    approve.add_argument("--run-id", required=True)
    approve.add_argument("--operation-ids", required=True)
    approve.add_argument("--provider-mode", default="fake", choices=["fake", "cli"])

    qa = sub.add_parser("qa")
    qa.add_argument("--question", required=True)

    args = parser.parse_args(argv)
    workspace = Path(args.workspace)

    if args.command == "process":
        ref = MeetingRef(
            type=MeetingRefType.LATEST_ENDED if args.latest_ended else MeetingRefType.TRANSCRIPT_FILE,
            value=args.transcript_file,
            query=args.query,
        )
        request = ProcessMeetingInput(
            meeting_ref=ref,
            provider_mode=args.provider_mode,
            analyzer_mode=args.analyzer_mode,
            create_doc=args.create_doc,
            create_tasks=args.create_tasks,
            send_message=args.send_message,
            chat_id=args.chat_id,
            dry_run=args.dry_run,
        )
        result = PostMeetingWorkflow(workspace, args.provider_mode, args.analyzer_mode).process(request)
        print(result.model_dump_json(indent=2))
        return 0
    if args.command == "approve":
        operation_ids = [part.strip() for part in args.operation_ids.split(",") if part.strip()]
        result = PostMeetingWorkflow(workspace, args.provider_mode, "fake").approve(args.run_id, operation_ids)
        print(result.model_dump_json(indent=2))
        return 0
    if args.command == "qa":
        print(json.dumps(MeetingMemoryStore(workspace).qa(args.question).model_dump(mode="json"), ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
