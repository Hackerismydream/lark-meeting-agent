"""Local developer CLI for the meeting MVP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.evals import LifecycleEvaluator
from nanobot.meeting.live import LiveMeetingWorkflow
from nanobot.meeting.live_lark import LiveLarkMeetingWorkflow
from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.schemas import (
    ApprovalStatus,
    LiveEventKind,
    LiveMeetingEvent,
    MeetingRef,
    MeetingRefType,
    MeetingType,
    PreBriefInput,
    ProcessMeetingInput,
)
from nanobot.meeting.transcript_gate import TranscriptGateWorkflow
from nanobot.meeting.workflow import PostMeetingWorkflow

PROVIDER_MODE_CHOICES = ["fake", "cli", "oapi"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m nanobot.meeting.cli")
    parser.add_argument("--workspace", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    process = sub.add_parser("process")
    process.add_argument("--latest-ended", action="store_true")
    process.add_argument("--query")
    process.add_argument("--transcript-file")
    process.add_argument("--provider-mode", default="fake", choices=PROVIDER_MODE_CHOICES)
    process.add_argument("--analyzer-mode", default="fake", choices=["fake", "llm"])
    process.add_argument("--create-doc", action="store_true")
    process.add_argument("--create-tasks", action="store_true")
    process.add_argument("--send-message", action="store_true")
    process.add_argument("--chat-id")
    process.add_argument("--dry-run", action="store_true", default=True)

    approve = sub.add_parser("approve")
    approve.add_argument("--run-id", required=True)
    approve.add_argument("--operation-ids", required=True)
    approve.add_argument("--provider-mode", choices=PROVIDER_MODE_CHOICES)
    approve.add_argument("--override-provider-mode", action="store_true")

    qa = sub.add_parser("qa")
    qa.add_argument("--question", required=True)

    prebrief = sub.add_parser("prebrief")
    prebrief.add_argument("--query")
    prebrief.add_argument("--meeting-id")
    prebrief.add_argument("--meeting-type", default="general", choices=[item.value for item in MeetingType])
    prebrief.add_argument("--project")
    prebrief.add_argument("--customer")
    prebrief.add_argument("--provider-mode", default="fake", choices=PROVIDER_MODE_CHOICES)

    transcript_gate = sub.add_parser("transcript-gate")
    transcript_gate.add_argument("--query")
    transcript_gate.add_argument("--start")
    transcript_gate.add_argument("--end")
    transcript_gate.add_argument("--provider-mode", default="cli", choices=PROVIDER_MODE_CHOICES)
    transcript_gate.add_argument("--limit", type=int, default=10)

    live_start = sub.add_parser("live-start")
    live_start.add_argument("--meeting-id", required=True)
    live_start.add_argument("--title", default="live meeting")

    live_join = sub.add_parser("live-join")
    live_join.add_argument("--meeting-number", required=True)
    live_join.add_argument("--password")
    live_join.add_argument("--title", default="live meeting")
    live_join.add_argument("--provider-mode", default="fake", choices=PROVIDER_MODE_CHOICES)
    live_join.add_argument("--approve-visible-join", action="store_true")

    live_ingest = sub.add_parser("live-ingest")
    live_ingest.add_argument("--live-run-id", required=True)
    live_ingest.add_argument("--meeting-id", required=True)
    live_ingest.add_argument("--text", required=True)
    live_ingest.add_argument("--speaker")
    live_ingest.add_argument("--timestamp")
    live_ingest.add_argument("--kind", default="transcript_delta", choices=[item.value for item in LiveEventKind])

    live_qa = sub.add_parser("live-qa")
    live_qa.add_argument("--live-run-id", required=True)
    live_qa.add_argument("--question", required=True)

    live_poll = sub.add_parser("live-poll")
    live_poll.add_argument("--meeting-id", required=True)
    live_poll.add_argument("--live-run-id", required=True)
    live_poll.add_argument("--provider-mode", default="fake", choices=PROVIDER_MODE_CHOICES)
    live_poll.add_argument("--page-token")
    live_poll.add_argument("--no-page-all", action="store_true")
    live_poll.add_argument("--start")
    live_poll.add_argument("--end")

    live_leave = sub.add_parser("live-leave")
    live_leave.add_argument("--meeting-id", required=True)
    live_leave.add_argument("--provider-mode", default="fake", choices=PROVIDER_MODE_CHOICES)
    live_leave.add_argument("--approve-visible-leave", action="store_true")

    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--cases", default="tests/fixtures/meeting/evaluation/lifecycle_cases.json")
    evaluate.add_argument("--output")

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
        result = PostMeetingWorkflow(workspace, args.provider_mode or "fake", "fake").approve(
            args.run_id,
            operation_ids,
            provider_mode=args.provider_mode,
            override_provider_mode=args.override_provider_mode,
        )
        print(result.model_dump_json(indent=2))
        return 0
    if args.command == "qa":
        print(json.dumps(MeetingMemoryStore(workspace).qa(args.question).model_dump(mode="json"), ensure_ascii=False, indent=2))
        return 0
    if args.command == "prebrief":
        ref = MeetingRef(
            type=MeetingRefType.MEETING_ID if args.meeting_id else MeetingRefType.LATEST_ENDED,
            value=args.meeting_id,
            query=args.query,
        )
        result = PreBriefWorkflow(workspace, args.provider_mode).generate(
            PreBriefInput(
                meeting_ref=ref,
                provider_mode=args.provider_mode,
                meeting_type=MeetingType(args.meeting_type),
                project=args.project,
                customer=args.customer,
            )
        )
        print(result.model_dump_json(indent=2))
        return 0
    if args.command == "transcript-gate":
        result = TranscriptGateWorkflow(workspace).run(
            query=args.query,
            start=args.start,
            end=args.end,
            provider_mode=args.provider_mode,
            limit=args.limit,
        )
        print(result.model_dump_json(indent=2))
        return 0
    if args.command == "live-start":
        print(LiveMeetingWorkflow(workspace).start(args.meeting_id, args.title).model_dump_json(indent=2))
        return 0
    if args.command == "live-join":
        approved = ApprovalStatus.APPROVED if args.approve_visible_join else ApprovalStatus.PENDING
        result = LiveLarkMeetingWorkflow(workspace, args.provider_mode).join(
            meeting_number=args.meeting_number,
            password=args.password,
            title=args.title,
            dry_run=not args.approve_visible_join,
            approval_status=approved,
        )
        print(result.model_dump_json(indent=2))
        return 0
    if args.command == "live-ingest":
        event = LiveMeetingEvent(
            event_id="cli-event",
            live_run_id=args.live_run_id,
            meeting_id=args.meeting_id,
            kind=LiveEventKind(args.kind),
            text=args.text,
            speaker_name=args.speaker,
            timestamp=args.timestamp,
        )
        print(LiveMeetingWorkflow(workspace).ingest(event).model_dump_json(indent=2))
        return 0
    if args.command == "live-qa":
        print(LiveMeetingWorkflow(workspace).qa(args.live_run_id, args.question).model_dump_json(indent=2))
        return 0
    if args.command == "live-poll":
        result = LiveLarkMeetingWorkflow(workspace, args.provider_mode).poll(
            args.meeting_id,
            live_run_id=args.live_run_id,
            page_token=args.page_token,
            page_all=not args.no_page_all,
            start=args.start,
            end=args.end,
        )
        print(result.model_dump_json(indent=2))
        return 0
    if args.command == "live-leave":
        approved = ApprovalStatus.APPROVED if args.approve_visible_leave else ApprovalStatus.PENDING
        result = LiveLarkMeetingWorkflow(workspace, args.provider_mode).leave(
            args.meeting_id,
            dry_run=not args.approve_visible_leave,
            approval_status=approved,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.command == "evaluate":
        report = LifecycleEvaluator(workspace).evaluate_file(args.cases, args.output)
        print(report.model_dump_json(indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
