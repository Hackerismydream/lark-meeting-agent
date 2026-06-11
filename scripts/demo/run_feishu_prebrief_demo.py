from __future__ import annotations

import argparse
from pathlib import Path

from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.schemas import MeetingRef, MeetingRefType, MeetingType, PreBriefInput, ProviderMode
from nanobot.meeting_data.feishu_wrapper import fixture_to_feishu_context
from nanobot.meeting_data.fixture_store import write_jsonl

from scripts.demo.feishu_demo_common import append_command_log, load_fixture_for_demo, sanitize, scenario_dir, write_blocker, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Real Feishu calendar -> prebrief sandbox evidence demo.")
    parser.add_argument("--fixtures", default="data/processed/meeting_fixtures")
    parser.add_argument("--fixture-id", default=None)
    parser.add_argument("--query", default="项目例会")
    parser.add_argument("--provider-mode", default="cli", choices=[mode.value for mode in ProviderMode])
    parser.add_argument("--out-root", default="runs/real_feishu_scenarios")
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    run_dir = scenario_dir(args.out_root, "scenario_01_prebrief")
    append_command_log(run_dir / "command.log", "run_feishu_prebrief_demo", vars(args))
    adapter = _adapter(args.provider_mode, run_dir)
    try:
        calendar = adapter.execute("calendar.agenda", {"query": args.query}, dry_run=False)
    except Exception as exc:
        write_blocker(run_dir / "blocker.md", "calendar agenda failed", exc)
        print(f"wrote blocker to {run_dir / 'blocker.md'}")
        return 0

    sanitized_calendar = sanitize(calendar)
    (run_dir / "blocker.md").unlink(missing_ok=True)
    write_json(run_dir / "calendar_event_sanitized.json", sanitized_calendar)
    selected = _first_event(calendar) or {"meeting_id": "no-event", "title": args.query}
    fixture = load_fixture_for_demo(args.fixtures, args.fixture_id)
    context = fixture_to_feishu_context(fixture)
    brief = PreBriefWorkflow(run_dir / "memory", provider_mode=ProviderMode.FAKE.value).generate(
        PreBriefInput(
            meeting_ref=MeetingRef(type=MeetingRefType.MEETING_ID, value=str(selected.get("meeting_id") or "calendar-event"), query=str(selected.get("title") or args.query)),
            provider_mode=ProviderMode.FAKE,
            meeting_type=MeetingType.PROJECT_SYNC,
            project=fixture.meta.domain or fixture.dataset.value,
            customer=fixture.meta.city,
            participants=[participant.name for participant in context.participants],
        )
    )
    _write_prebrief(run_dir / "prebrief.md", brief, fixture.fixture_id)
    write_jsonl(
        [
            {"event_type": "real_lark_read", "operation": "calendar.agenda"},
            {"event_type": "artifact_created", "path": "prebrief.md"},
        ],
        run_dir / "trace.jsonl",
    )
    (run_dir / "evidence.md").write_text(
        "\n".join(
            [
                "# Prebrief Evidence",
                "",
                "- scenario: real Feishu calendar to prebrief",
                "- real_lark_read: true",
                "- real_lark_write: false",
                f"- fixture_id: `{fixture.fixture_id}`",
                "- dry_run: true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote prebrief evidence to {run_dir}")
    return 0


def _adapter(provider_mode: str, run_dir: Path) -> LarkToolAdapter:
    if ProviderMode(provider_mode) == ProviderMode.FAKE:
        return LarkToolAdapter.fake(run_dir)
    if ProviderMode(provider_mode) == ProviderMode.OAPI:
        return LarkToolAdapter.oapi(run_dir)
    return LarkToolAdapter.cli(run_dir)


def _first_event(payload: dict) -> dict | None:
    for key in ("items", "events", "meetings"):
        value = payload.get(key)
        if isinstance(value, list) and value:
            return value[0] if isinstance(value[0], dict) else None
    data = payload.get("data")
    return _first_event(data) if isinstance(data, dict) else None


def _write_prebrief(path: Path, brief, fixture_id: str) -> None:
    lines = [f"# {brief.meeting.title if brief.meeting else 'Prebrief'}", "", brief.goal, "", f"Fixture: `{fixture_id}`"]
    for section in brief.sections:
        lines.extend(["", f"## {section.title}"])
        lines.extend(f"- {bullet}" for bullet in section.bullets)
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
