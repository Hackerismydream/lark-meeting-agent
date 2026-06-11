from __future__ import annotations

import argparse
from pathlib import Path

from nanobot.meeting.renderers import render_minutes_markdown
from nanobot.meeting.schemas import ApprovalStatus, ProviderMode
from nanobot.meeting.workflow import PostMeetingWorkflow
from nanobot.meeting_data.fixture_store import write_jsonl

from scripts.demo.feishu_demo_common import (
    append_command_log,
    load_fixture_for_demo,
    real_writes_enabled,
    sandbox_chat_id,
    sandbox_doc_folder_token,
    scenario_dir,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Public transcript fixture -> postmeeting WritePlan -> sandbox Feishu evidence demo.")
    parser.add_argument("--fixtures", default="data/processed/meeting_fixtures")
    parser.add_argument("--fixture-id", default=None)
    parser.add_argument("--provider-mode", default="fake", choices=[mode.value for mode in ProviderMode])
    parser.add_argument("--out-root", default="runs/real_feishu_scenarios")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args()

    run_dir = scenario_dir(args.out_root, "scenario_02_postmeeting_writeback")
    append_command_log(run_dir / "command.log", "run_feishu_postmeeting_demo", vars(args))
    fixture = load_fixture_for_demo(args.fixtures, args.fixture_id)
    write_json(run_dir / "fixture.json", {"fixture_id": fixture.fixture_id, "dataset": fixture.dataset.value, "provenance": fixture.provenance.model_dump(mode="json")})
    transcript_path = run_dir / "transcript.txt"
    transcript_path.write_text("\n".join(f"{turn.speaker or 'speaker'}: {turn.text}" for turn in fixture.transcript_turns), encoding="utf-8")

    chat_id = sandbox_chat_id()
    workflow = PostMeetingWorkflow(run_dir / "memory", provider_mode=args.provider_mode, analyzer_mode="fake")
    result = workflow.process_transcript_file(
        transcript_path,
        create_doc=True,
        create_tasks=True,
        send_message=True,
        chat_id=chat_id,
        dry_run=True,
        provider_mode=args.provider_mode,
        analyzer_mode="fake",
    )
    if result.minutes and result.meeting:
        (run_dir / "minutes.md").write_text(render_minutes_markdown(result.meeting, result.minutes), encoding="utf-8")
        write_json(run_dir / "decisions.json", [item.model_dump(mode="json") for item in result.minutes.decisions])
        write_json(run_dir / "action_items.json", [item.model_dump(mode="json") for item in result.minutes.action_items])
    write_json(run_dir / "write_plan.json", result.write_plan.model_dump(mode="json") if result.write_plan else {})
    approval_ids = _approvable_operation_ids(result.write_plan)
    (run_dir / "approval_prompt.md").write_text(_approval_prompt(approval_ids, args.approve), encoding="utf-8")

    approved: list[str] = []
    write_results = {"enabled": False, "results": []}
    if args.approve and real_writes_enabled() and result.write_plan:
        run = workflow.memory.load_run_snapshot(result.run_id)
        _inject_sandbox_targets(run)
        workflow.memory.save_run_snapshot(run)
        approved = approval_ids
        approved_result = workflow.approve(result.run_id, approved, provider_mode=args.provider_mode)
        write_results = {"enabled": True, "result": approved_result.model_dump(mode="json")}
    write_json(run_dir / "approved_operations.json", approved)
    write_json(run_dir / "lark_write_results_sanitized.json", write_results)
    write_jsonl([{"event_type": "write_plan_generated"}, {"event_type": "real_write_enabled", "value": bool(approved)}], run_dir / "trace.jsonl")
    (run_dir / "evidence.md").write_text(
        "\n".join(
            [
                "# Postmeeting Writeback Evidence",
                "",
                f"- fixture_id: `{fixture.fixture_id}`",
                f"- real_writes_enabled: `{real_writes_enabled()}`",
                f"- approved: `{bool(approved)}`",
                f"- chat_target_present: `{bool(chat_id)}`",
                "- public fixture supplies transcript content.",
                "- LarkToolAdapter / WritePlan supplies write boundary.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote postmeeting evidence to {run_dir}")
    return 0


def _approvable_operation_ids(write_plan) -> list[str]:
    if not write_plan:
        return []
    return [
        operation.operation_id
        for operation in write_plan.operations
        if operation.approval_status != ApprovalStatus.MISSING_TARGET
    ]


def _inject_sandbox_targets(run) -> None:
    folder = sandbox_doc_folder_token()
    for operation in run.write_plan.operations if run.write_plan else []:
        if operation.operation_type.value == "docs.create" and folder:
            operation.dry_run_payload["folder_token"] = folder


def _approval_prompt(operation_ids: list[str], approve_requested: bool) -> str:
    return "\n".join(
        [
            "# Approval Prompt",
            "",
            "Real writes require both `--approve` and `LMA_DEMO_ENABLE_REAL_WRITES=1`.",
            f"Approve requested: `{approve_requested}`",
            "",
            "Operations eligible for approval:",
            *[f"- `{operation_id}`" for operation_id in operation_ids],
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
