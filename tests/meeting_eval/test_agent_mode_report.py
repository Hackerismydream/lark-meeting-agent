from __future__ import annotations

import json
from pathlib import Path

from tests.meeting_eval.test_eval_runner_agent_mode import _prepare_toy_fixtures
from nanobot.meeting_eval.runner import run_suite


def test_agent_mode_report_marks_public_corpus_scope(tmp_path) -> None:
    result = run_suite("tiny30", _prepare_toy_fixtures(tmp_path), tmp_path / "runs", mode="agent")
    report = json.loads(Path(result["outputs"]["report"]).read_text(encoding="utf-8"))

    assert report["metadata"]["metric_scope"] == "public_corpus_development"
    assert report["metadata"]["used_real_llm"] is False
    assert report["metrics"]["write_plan_dry_run_rate"] == 1.0
    assert report["metrics"]["workflow_completion_rate"] == 1.0
