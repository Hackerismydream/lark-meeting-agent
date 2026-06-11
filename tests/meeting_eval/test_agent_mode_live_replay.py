from __future__ import annotations

from pathlib import Path

from tests.meeting_eval.test_eval_runner_agent_mode import _prepare_toy_fixtures
from nanobot.meeting_data.fixture_store import read_jsonl
from nanobot.meeting_eval.runner import run_suite


def test_agent_mode_generates_live_replay_artifacts(tmp_path) -> None:
    result = run_suite("tiny30", _prepare_toy_fixtures(tmp_path), tmp_path / "runs", mode="agent")
    fixture_dirs = [path for path in Path(result["out_dir"]).iterdir() if path.is_dir()]

    snapshots = fixture_dirs[0] / "artifacts" / "live_state_snapshots.jsonl"
    live_answers = fixture_dirs[0] / "artifacts" / "live_qa_answers.jsonl"
    assert read_jsonl(snapshots)
    assert read_jsonl(live_answers)
