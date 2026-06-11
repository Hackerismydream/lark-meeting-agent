from __future__ import annotations

import json
from pathlib import Path

from tests.meeting_eval.test_eval_runner_agent_mode import _prepare_toy_fixtures
from nanobot.meeting_eval.runner import run_suite


def test_agent_mode_generates_postmeeting_write_plan(tmp_path) -> None:
    result = run_suite("tiny30", _prepare_toy_fixtures(tmp_path), tmp_path / "runs", mode="agent")
    fixture_dirs = [path for path in Path(result["out_dir"]).iterdir() if path.is_dir()]

    artifacts = fixture_dirs[0] / "artifacts"
    write_plan = json.loads((artifacts / "write_plan.json").read_text(encoding="utf-8"))
    assert (artifacts / "minutes.md").exists()
    assert write_plan["operations"]
    assert all(operation["dry_run_payload"] for operation in write_plan["operations"])
    assert all(operation["execution_status"] == "pending" for operation in write_plan["operations"])
