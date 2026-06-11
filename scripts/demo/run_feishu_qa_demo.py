from __future__ import annotations

import argparse

from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.schemas import ApprovalStatus, ProviderMode
from nanobot.meeting_data.fixture_store import load_fixtures, write_jsonl

from scripts.demo.feishu_demo_common import append_command_log, real_writes_enabled, sandbox_chat_id, scenario_dir, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Meeting memory -> source-grounded QA -> optional sandbox message evidence demo.")
    parser.add_argument("--fixtures", default="data/processed/meeting_fixtures")
    parser.add_argument("--question", default="What evidence supports the meeting summary?")
    parser.add_argument("--provider-mode", default="fake", choices=[mode.value for mode in ProviderMode])
    parser.add_argument("--out-root", default="runs/real_feishu_scenarios")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args()

    run_dir = scenario_dir(args.out_root, "scenario_03_qa")
    append_command_log(run_dir / "command.log", "run_feishu_qa_demo", vars(args))
    fixtures = load_fixtures(args.fixtures)
    if not fixtures:
        raise SystemExit(f"no MeetingFixture JSON found under {args.fixtures}")
    memory_seed = [{"fixture_id": fixture.fixture_id, "dataset": fixture.dataset.value} for fixture in fixtures[:10]]
    write_json(run_dir / "memory_seed.json", memory_seed)

    answers = []
    sources = []
    for fixture in fixtures[:5]:
        selected_turns = fixture.transcript_turns[:2]
        fixture_sources = [
            {
                "fixture_id": fixture.fixture_id,
                "meeting_id": fixture.fixture_id,
                "turn_id": turn.turn_id,
                "speaker": turn.speaker,
                "timestamp": turn.start_time or turn.start_sec,
                "text": turn.text,
            }
            for turn in selected_turns
        ]
        sources.extend(fixture_sources)
        answers.append(
            {
                "question": args.question,
                "answer": "Found source-backed fixture evidence." if fixture_sources else "insufficient evidence",
                "sufficient": bool(fixture_sources),
                "sources": fixture_sources,
            }
        )
    write_jsonl(answers, run_dir / "qa_answers.jsonl")
    write_jsonl(sources, run_dir / "qa_sources.jsonl")

    chat_id = sandbox_chat_id()
    write_plan = {
        "operations": [
            {
                "operation_id": "op-im-qa-1",
                "operation_type": "im.send",
                "approval_status": "pending" if chat_id else "missing_target",
                "execution_status": "pending",
                "dry_run_payload": {"chat_id": chat_id, "markdown": _qa_message(answers[:3])},
            }
        ]
    }
    write_json(run_dir / "optional_write_plan.json", write_plan)
    if args.approve and real_writes_enabled() and chat_id:
        adapter = _adapter(args.provider_mode, run_dir)
        result = adapter.execute("im.send", write_plan["operations"][0]["dry_run_payload"], dry_run=False, approval_status=ApprovalStatus.APPROVED)
        write_json(run_dir / "lark_write_results_sanitized.json", result)
    write_jsonl([{"event_type": "qa_generated"}, {"event_type": "optional_write_plan_generated"}], run_dir / "trace.jsonl")
    (run_dir / "evidence.md").write_text(
        "# QA Evidence\n\n- QA answers include sources or insufficient evidence.\n- Optional sandbox message requires approval and env gate.\n",
        encoding="utf-8",
    )
    print(f"wrote QA evidence to {run_dir}")
    return 0


def _qa_message(answers: list[dict]) -> str:
    lines = ["# Meeting QA demo"]
    for answer in answers:
        lines.append(f"- {answer['answer']} sources={len(answer['sources'])}")
    return "\n".join(lines)


def _adapter(provider_mode: str, run_dir):
    if ProviderMode(provider_mode) == ProviderMode.FAKE:
        return LarkToolAdapter.fake(run_dir)
    if ProviderMode(provider_mode) == ProviderMode.OAPI:
        return LarkToolAdapter.oapi(run_dir)
    return LarkToolAdapter.cli(run_dir)


if __name__ == "__main__":
    raise SystemExit(main())
