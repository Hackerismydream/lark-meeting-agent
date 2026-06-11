from __future__ import annotations

from pathlib import Path

from nanobot.meeting_data.adapters.meetingbank import prepare_tiny10 as prepare_meetingbank
from nanobot.meeting_data.adapters.qmsum import prepare_tiny10 as prepare_qmsum
from nanobot.meeting_data.adapters.vcsum import prepare_tiny10 as prepare_vcsum
from nanobot.meeting_eval.runner import run_suite


def test_eval_runner_smoke_on_toy_fixtures(tmp_path) -> None:
    fixtures = tmp_path / "fixtures"
    prepare_meetingbank(Path("tests/fixtures/meeting_data/raw_samples/meetingbank"), fixtures / "meetingbank" / "tiny10", tmp_path / "mb.jsonl")
    prepare_qmsum(Path("tests/fixtures/meeting_data/raw_samples/qmsum"), fixtures / "qmsum" / "tiny10", tmp_path / "qm.jsonl")
    prepare_vcsum(Path("tests/fixtures/meeting_data/raw_samples/vcsum"), fixtures / "vcsum" / "tiny10", tmp_path / "vc.jsonl")

    result = run_suite("tiny30", fixtures, tmp_path / "runs")

    out_dir = Path(result["out_dir"])
    assert result["fixtures"] == 3
    assert (out_dir / "report.json").exists()
    assert (out_dir / "trace.jsonl").exists()
    assert (out_dir / "predictions.jsonl").exists()
    assert (out_dir / "failures.jsonl").exists()
