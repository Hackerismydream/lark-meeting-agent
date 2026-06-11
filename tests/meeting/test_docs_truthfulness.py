from __future__ import annotations

import re
from pathlib import Path


V1_DOCS = [
    Path("docs/V1_RELEASE_REPORT.md"),
    Path("docs/V1_BENCHMARK_REPORT.md"),
    Path("docs/V1_DEMO_RUNBOOK.md"),
    Path("docs/V1_KNOWN_LIMITATIONS.md"),
    Path("docs/V1_RESUME_AND_INTERVIEW_NOTES.md"),
]


def test_v1_docs_exist_and_include_release_separations() -> None:
    text = "\n".join(path.read_text() for path in V1_DOCS)

    assert "Deterministic Fixture Metrics" in text
    assert "Optional Real LLM Metrics" in text
    assert "Real Lark Smoke" in text
    assert "Blocked/unverified" in text
    assert re.search(r"Commit: `?[0-9a-f]{7,40}`?", text)


def test_v1_docs_do_not_claim_unverified_production_or_apps() -> None:
    text = "\n".join(path.read_text().lower() for path in V1_DOCS)
    banned = [
        "production deployed",
        "real feishu channel verified",
        "asr implemented",
        "macos companion app is implemented",
        "real live meeting smoke passed",
    ]

    assert all(phrase not in text for phrase in banned)
    assert "no custom asr" in text
    assert "no macos companion app" in text
    assert "not claimed" in text or "not claim" in text


def test_benchmark_report_distinguishes_fixture_from_real_llm() -> None:
    text = Path("docs/V1_BENCHMARK_REPORT.md").read_text()

    assert "deterministic fake analyzer/provider" in text
    assert "Do not treat deterministic fake metrics as real LLM quality metrics." in text
    assert "not claim a real meeting join/poll/QA/leave success" in text
