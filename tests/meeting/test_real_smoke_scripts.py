from __future__ import annotations

import json
from pathlib import Path

from nanobot.meeting.cli import main
from nanobot.meeting.live_lark import classify_live_smoke_error


def test_live_smoke_without_meeting_number_gives_clear_error(tmp_path: Path, capsys) -> None:
    exit_code = main(["--workspace", str(tmp_path), "live-smoke", "--provider-mode", "fake"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "missing_meeting_number"
    assert "--meeting-number is required" in output["error"]


def test_live_smoke_dry_run_does_not_join(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "--workspace",
            str(tmp_path),
            "live-smoke",
            "--provider-mode",
            "fake",
            "--meeting-number",
            "123456789",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "dry_run"
    assert output["meeting_id"] is None
    assert not (tmp_path / ".lark_meeting_agent" / "live_states").exists()


def test_live_smoke_fake_real_path_can_export_sanitized_shapes(tmp_path: Path, capsys) -> None:
    export_path = tmp_path / "raw-shapes.json"

    exit_code = main(
        [
            "--workspace",
            str(tmp_path),
            "live-smoke",
            "--provider-mode",
            "fake",
            "--meeting-number",
            "123456789",
            "--approve-visible-join",
            "--approve-visible-leave",
            "--export-raw-event-shapes",
            str(export_path),
        ]
    )

    output = json.loads(capsys.readouterr().out)
    shapes = json.loads(export_path.read_text())
    assert exit_code == 0
    assert output["status"] == "completed"
    assert output["event_count"] >= 1
    assert output["raw_event_shape_path"] == str(export_path)
    assert shapes["events"]
    assert "Alice 决定" not in export_path.read_text()


def test_live_smoke_failure_classification() -> None:
    assert classify_live_smoke_error("missing required scope vc:meeting.bot.join:write") == "permission"
    assert classify_live_smoke_error("ErrNotInGray") == "gray"
    assert classify_live_smoke_error("bot is not in meeting") == "not_in_meeting"
    assert classify_live_smoke_error("meeting_status_MEETING_END") == "meeting_ended"
    assert classify_live_smoke_error("bad page_token") == "page_token_issue"


def test_lma_real_exposes_live_smoke_without_requiring_process_llm_key() -> None:
    script = Path("scripts/lma-real").read_text()

    assert "live-smoke" in script
    assert '[[ "$subcommand" == "process"' in script
