"""Evaluation report writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nanobot.meeting_data.fixture_store import write_jsonl
from nanobot.meeting_eval.tasks import EvalPrediction


def write_eval_outputs(
    out_dir: Path | str,
    metrics: dict[str, Any],
    predictions: list[EvalPrediction],
    failures: list[dict[str, Any]],
) -> dict[str, Path]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    report_path = root / "report.json"
    report_path.write_text(json.dumps({"metrics": metrics, "failures": failures}, ensure_ascii=False, indent=2), encoding="utf-8")
    trace_path = write_jsonl(
        [
            {"event_type": "eval_observation", "message": "suite_report_written", "data": {"metrics": sorted(metrics)}},
            {"event_type": "artifact_created", "message": "report.json", "data": {"path": str(report_path)}},
        ],
        root / "trace.jsonl",
    )
    predictions_path = write_jsonl([prediction.model_dump(mode="json") for prediction in predictions], root / "predictions.jsonl")
    failures_path = write_jsonl(failures, root / "failures.jsonl")
    return {
        "report": report_path,
        "trace": trace_path,
        "predictions": predictions_path,
        "failures": failures_path,
    }
