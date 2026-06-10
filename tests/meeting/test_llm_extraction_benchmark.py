from __future__ import annotations

import os
from pathlib import Path

import pytest

from nanobot.meeting.analyzer import OpenAICompatibleMeetingAnalyzer
from nanobot.meeting.evals import LifecycleEvaluator
from nanobot.meeting.evidence import EvidenceIntegrityValidator
from nanobot.meeting.normalizer import TranscriptNormalizer

CASES = Path("tests/fixtures/meeting/evaluation/llm_extraction_cases.json")


def test_llm_extraction_benchmark_fixtures_have_expected_labels(tmp_path: Path) -> None:
    cases = LifecycleEvaluator(tmp_path).load_cases(CASES)

    assert len(cases) == 5
    assert all(case.expected.decisions for case in cases)
    assert all(case.expected.action_items for case in cases)
    assert all(case.expected.evidence_segment_ids for case in cases)


@pytest.mark.skipif(os.environ.get("RUN_REAL_LLM_TESTS") != "1", reason="real LLM benchmark is opt-in")
def test_optional_llm_extraction_benchmark_runs_when_enabled(tmp_path: Path) -> None:
    cases = LifecycleEvaluator(tmp_path).load_cases(CASES)
    analyzer = OpenAICompatibleMeetingAnalyzer()
    normalizer = TranscriptNormalizer()
    validator = EvidenceIntegrityValidator()

    for case in cases:
        segments = normalizer.normalize_text(case.case_id, case.transcript)
        minutes = analyzer.analyze(case.case_id, case.case_id, segments)
        validated = validator.validate_minutes(minutes, segments)
        produced_segments = {
            evidence.segment_id
            for item in [*validated.decisions, *validated.action_items]
            for evidence in item.evidence_refs
        }
        assert set(case.expected.evidence_segment_ids).issubset(produced_segments)
