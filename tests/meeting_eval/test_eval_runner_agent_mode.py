from __future__ import annotations

import json
from pathlib import Path

from nanobot.meeting_data.adapters.meetingbank import prepare_tiny10 as prepare_meetingbank
from nanobot.meeting_data.adapters.qmsum import prepare_tiny10 as prepare_qmsum
from nanobot.meeting_data.adapters.vcsum import prepare_tiny10 as prepare_vcsum
from nanobot.meeting_eval.runner import run_suite


def _prepare_toy_fixtures(tmp_path: Path) -> Path:
    fixtures = tmp_path / "fixtures"
    prepare_meetingbank(Path("tests/fixtures/meeting_data/raw_samples/meetingbank"), fixtures / "meetingbank" / "tiny10", tmp_path / "mb.jsonl")
    prepare_qmsum(Path("tests/fixtures/meeting_data/raw_samples/qmsum"), fixtures / "qmsum" / "tiny10", tmp_path / "qm.jsonl")
    prepare_vcsum(Path("tests/fixtures/meeting_data/raw_samples/vcsum"), fixtures / "vcsum" / "tiny10", tmp_path / "vc.jsonl")
    return fixtures


def test_agent_mode_runs_toy_fixtures(tmp_path) -> None:
    result = run_suite("tiny30", _prepare_toy_fixtures(tmp_path), tmp_path / "runs", mode="agent")

    report = json.loads(Path(result["outputs"]["report"]).read_text(encoding="utf-8"))
    assert result["mode"] == "agent"
    assert result["fixtures"] == 3
    assert result["failures"] == []
    assert report["metadata"]["metric_scope"] == "public_corpus_development"
    assert report["metadata"]["used_real_lark"] is False
    assert report["metadata"]["real_writes"] is False


def test_mock_smoke_mode_still_runs(tmp_path) -> None:
    result = run_suite("tiny30", _prepare_toy_fixtures(tmp_path), tmp_path / "runs", mode="mock_smoke")

    assert result["mode"] == "mock_smoke"
    assert result["fixtures"] == 3
    assert Path(result["outputs"]["report"]).exists()
