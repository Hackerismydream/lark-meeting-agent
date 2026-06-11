from __future__ import annotations

from nanobot.meeting_data.fixture_store import read_jsonl
from nanobot.meeting_eval.report import write_eval_outputs
from nanobot.meeting_eval.tasks import EvalPrediction


def test_report_outputs_expected_files(tmp_path) -> None:
    paths = write_eval_outputs(
        tmp_path,
        {"schema_valid_rate": 1.0},
        [EvalPrediction(task_id="t", fixture_id="f", dataset="qmsum", task_type="qa")],
        [],
    )

    assert paths["report"].exists()
    assert paths["trace"].exists()
    assert paths["predictions"].exists()
    assert paths["failures"].exists()
    assert read_jsonl(paths["predictions"])[0]["task_id"] == "t"
