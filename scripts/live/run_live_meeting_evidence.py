from __future__ import annotations

import argparse

from nanobot.meeting.live_evidence import LiveMeetingEvidenceRunner


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real live meeting evidence collection.")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--meeting-number", required=True)
    parser.add_argument("--provider-mode", default="cli", choices=["fake", "cli", "oapi"])
    parser.add_argument("--out-root", default="runs/live_real")
    parser.add_argument("--approve-visible-join", action="store_true")
    parser.add_argument("--approve-visible-leave", action="store_true")
    args = parser.parse_args()
    report = LiveMeetingEvidenceRunner(
        args.workspace,
        provider_mode=args.provider_mode,
        out_root=args.out_root,
    ).run(
        args.meeting_number,
        approve_visible_join=args.approve_visible_join,
        approve_visible_leave=args.approve_visible_leave,
    )
    print(report.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
