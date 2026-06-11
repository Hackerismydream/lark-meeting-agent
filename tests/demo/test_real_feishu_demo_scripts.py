from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from nanobot.meeting_data.adapters.meetingbank import prepare_tiny10 as prepare_meetingbank
from nanobot.meeting_data.fixture_store import read_jsonl
from scripts.demo.feishu_demo_common import load_fixture_for_demo, sanitize
from scripts.demo.run_feishu_postmeeting_demo import main as postmeeting_main
from scripts.demo.run_feishu_prebrief_demo import main as prebrief_main
from scripts.demo.run_feishu_qa_demo import main as qa_main


def _prepare_toy_fixtures(tmp_path: Path) -> Path:
    fixtures = tmp_path / "fixtures"
    prepare_meetingbank(Path("tests/fixtures/meeting_data/raw_samples/meetingbank"), fixtures / "meetingbank" / "tiny10", tmp_path / "mb.jsonl")
    return fixtures


def test_prebrief_cli_missing_lark_writes_blocker(tmp_path, monkeypatch) -> None:
    fixtures = _prepare_toy_fixtures(tmp_path)
    out = tmp_path / "runs"
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_feishu_prebrief_demo.py",
            "--provider-mode",
            "cli",
            "--fixtures",
            str(fixtures),
            "--out-root",
            str(out),
        ],
    )

    assert prebrief_main() == 0
    blocker = out / "scenario_01_prebrief" / "blocker.md"
    assert blocker.exists()
    assert "calendar agenda failed" in blocker.read_text(encoding="utf-8")


def test_prebrief_fake_generates_evidence_pack(tmp_path, monkeypatch) -> None:
    fixtures = _prepare_toy_fixtures(tmp_path)
    out = tmp_path / "runs"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_feishu_prebrief_demo.py",
            "--provider-mode",
            "fake",
            "--fixtures",
            str(fixtures),
            "--out-root",
            str(out),
        ],
    )

    assert prebrief_main() == 0
    scenario = out / "scenario_01_prebrief"
    assert (scenario / "prebrief.md").exists()
    assert (scenario / "calendar_event_sanitized.json").exists()
    assert read_jsonl(scenario / "trace.jsonl")


def test_postmeeting_dry_run_does_not_execute_writes_and_marks_missing_chat(tmp_path, monkeypatch) -> None:
    fixtures = _prepare_toy_fixtures(tmp_path)
    out = tmp_path / "runs"
    monkeypatch.delenv("LMA_DEMO_ENABLE_REAL_WRITES", raising=False)
    monkeypatch.delenv("LMA_DEMO_CHAT_ID", raising=False)
    monkeypatch.delenv("LMA_DEMO_SANDBOX_CHAT_ID", raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_feishu_postmeeting_demo.py",
            "--provider-mode",
            "fake",
            "--fixtures",
            str(fixtures),
            "--out-root",
            str(out),
            "--dry-run",
        ],
    )

    assert postmeeting_main() == 0
    scenario = out / "scenario_02_postmeeting_writeback"
    write_plan = json.loads((scenario / "write_plan.json").read_text(encoding="utf-8"))
    im_ops = [operation for operation in write_plan["operations"] if operation["operation_type"] == "im.send"]
    assert im_ops
    assert im_ops[0]["approval_status"] == "missing_target"
    assert json.loads((scenario / "lark_write_results_sanitized.json").read_text(encoding="utf-8"))["enabled"] is False


def test_qa_demo_generates_sources_and_optional_write_plan(tmp_path, monkeypatch) -> None:
    fixtures = _prepare_toy_fixtures(tmp_path)
    out = tmp_path / "runs"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_feishu_qa_demo.py",
            "--provider-mode",
            "fake",
            "--fixtures",
            str(fixtures),
            "--out-root",
            str(out),
        ],
    )

    assert qa_main() == 0
    scenario = out / "scenario_03_qa"
    answers = read_jsonl(scenario / "qa_answers.jsonl")
    assert answers
    assert answers[0]["sources"]
    assert (scenario / "optional_write_plan.json").exists()


def test_sanitized_output_redacts_secrets() -> None:
    payload = {"access_token": "abc", "nested": {"chat_id": "oc_secret"}, "text": "Bearer abc.def"}

    assert sanitize(payload) == {"access_token": "[REDACTED]", "nested": {"chat_id": "[REDACTED]"}, "text": "[REDACTED]"}


def test_fixture_not_found_has_clear_error(tmp_path) -> None:
    fixtures = _prepare_toy_fixtures(tmp_path)

    with pytest.raises(SystemExit, match="fixture not found"):
        load_fixture_for_demo(fixtures, "missing-fixture")
