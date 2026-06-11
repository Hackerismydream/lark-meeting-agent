from __future__ import annotations

from pathlib import Path

from tests.meeting_eval.test_eval_runner_agent_mode import _prepare_toy_fixtures
from nanobot.meeting_eval.runner import run_suite


def test_agent_mode_generates_prebrief(tmp_path) -> None:
    result = run_suite("tiny30", _prepare_toy_fixtures(tmp_path), tmp_path / "runs", mode="agent")
    fixture_dirs = [path for path in Path(result["out_dir"]).iterdir() if path.is_dir()]

    prebrief = fixture_dirs[0] / "artifacts" / "prebrief.md"
    sources = fixture_dirs[0] / "artifacts" / "prebrief_sources.json"
    assert prebrief.exists()
    assert sources.exists()
    assert "#" in prebrief.read_text(encoding="utf-8")
