from __future__ import annotations

import json
from pathlib import Path

from nanobot.meeting.cli import main
from nanobot.meeting.live_evidence import LiveMeetingEvidenceRunner


def test_live_evidence_dry_run_writes_blocker_pack(tmp_path: Path) -> None:
    report = LiveMeetingEvidenceRunner(
        tmp_path,
        provider_mode="fake",
        out_root=tmp_path / "runs" / "live_real",
    ).run("123456789")

    run_dir = Path(report.run_dir)
    assert report.status == "dry_run"
    assert report.meeting_number == "123456789"
    assert report.blocker_path is not None
    assert "Rerun with --approve-visible-join" in report.next_actions[0]
    assert (run_dir / "join_dry_run.json").exists()
    assert (run_dir / "live_smoke_result.json").exists()
    assert (run_dir / "audit.jsonl").exists()
    assert (run_dir / "blocker.md").exists()
    dry_run = json.loads((run_dir / "join_dry_run.json").read_text())
    assert dry_run["session"]["meeting_number"] == "123456789"
    assert dry_run["provider_preview"] is not None
    assert json.loads((run_dir / "report.json").read_text())["status"] == "dry_run"


def test_live_evidence_fake_approved_path_exports_sanitized_shapes(tmp_path: Path) -> None:
    report = LiveMeetingEvidenceRunner(
        tmp_path,
        provider_mode="fake",
        out_root=tmp_path / "runs" / "live_real",
    ).run("123456789", approve_visible_join=True, approve_visible_leave=True)

    run_dir = Path(report.run_dir)
    assert report.status == "completed"
    assert report.blocker_path is None
    assert report.raw_event_shape_path is not None
    assert report.live_smoke_result_path is not None
    result = json.loads(Path(report.live_smoke_result_path).read_text())
    raw_shapes = Path(report.raw_event_shape_path).read_text()
    assert result["event_count"] >= 1
    assert "Alice 决定" not in raw_shapes
    assert json.loads(raw_shapes)["events"]
    assert (run_dir / "audit.jsonl").read_text()


def test_live_evidence_normalizes_spaced_meeting_number(tmp_path: Path) -> None:
    report = LiveMeetingEvidenceRunner(
        tmp_path,
        provider_mode="fake",
        out_root=tmp_path / "runs" / "live_real",
    ).run("909 401 086")

    assert report.meeting_number == "909401086"
    assert Path(report.run_dir).name == "909401086"


def test_live_evidence_rejects_invalid_meeting_number(tmp_path: Path) -> None:
    try:
        LiveMeetingEvidenceRunner(tmp_path, provider_mode="fake").run("12")
    except ValueError as exc:
        assert "exactly 9 digits" in str(exc)
    else:
        raise AssertionError("invalid meeting number was accepted")


def test_cli_live_evidence_writes_report(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "--workspace",
            str(tmp_path),
            "live-evidence",
            "--provider-mode",
            "fake",
            "--meeting-number",
            "123456789",
            "--out-root",
            str(tmp_path / "runs" / "live_real"),
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "dry_run"
    assert Path(output["run_dir"], "report.json").exists()
