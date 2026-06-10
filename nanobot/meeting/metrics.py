"""Deterministic meeting evaluation metrics."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import Field

from nanobot.meeting.schemas import MeetingBaseModel, QASource


class LiveReplayMetrics(MeetingBaseModel):
    action_item_precision: float = 1.0
    action_item_recall: float = 1.0
    decision_precision: float = 1.0
    decision_recall: float = 1.0
    evidence_coverage: float = 1.0
    evidence_grounding_accuracy: float = 1.0
    qa_source_accuracy: float = 1.0
    live_summary_freshness: float = 1.0
    owner_hallucination_rate: float = 0.0
    due_date_hallucination_rate: float = 0.0
    tool_call_safety_pass_rate: float = 1.0
    approval_bypass_rate: float = 0.0
    write_plan_correctness: float = 1.0
    regression_stability: float = 1.0
    duplicate_event_count: int = 0
    malformed_event_count: int = 0


class LiveReplayReport(MeetingBaseModel):
    profile: str = "deterministic-live-replay"
    scenario_count: int = 0
    metrics: LiveReplayMetrics = Field(default_factory=LiveReplayMetrics)
    failures: list[dict] = Field(default_factory=list)
    case_results: list[dict] = Field(default_factory=list)


class LifecycleReplayReport(MeetingBaseModel):
    profile: str = "deterministic-lifecycle-replay"
    scenario_count: int = 0
    prebrief_pass_rate: float = 0.0
    live_pass_rate: float = 0.0
    postmeeting_pass_rate: float = 0.0
    failures: list[dict] = Field(default_factory=list)


@dataclass(frozen=True)
class MatchCounts:
    true_positive: int
    false_positive: int
    false_negative: int


def compute_qa_source_accuracy(predicted: list[QASource], expected_segment_ids: list[str]) -> float:
    expected = {segment_id for segment_id in expected_segment_ids if segment_id}
    if not expected:
        return 1.0 if not predicted else 0.0
    predicted_ids = {source.segment_id for source in predicted if source.segment_id}
    return len(expected.intersection(predicted_ids)) / len(expected)


def precision_recall(predicted: list[str], expected: list[str]) -> tuple[float, float]:
    counts = match_counts(predicted, expected)
    precision = counts.true_positive / (counts.true_positive + counts.false_positive) if predicted else 1.0
    recall = counts.true_positive / (counts.true_positive + counts.false_negative) if expected else 1.0
    return precision, recall


def match_counts(predicted: list[str], expected: list[str]) -> MatchCounts:
    unmatched = list(expected)
    true_positive = 0
    for item in predicted:
        match = next((target for target in unmatched if similar_text(item, target)), None)
        if match:
            true_positive += 1
            unmatched.remove(match)
    return MatchCounts(
        true_positive=true_positive,
        false_positive=max(0, len(predicted) - true_positive),
        false_negative=len(unmatched),
    )


def similar_text(left: str, right: str) -> bool:
    left_norm = _normalize(left)
    right_norm = _normalize(right)
    if not left_norm or not right_norm:
        return left_norm == right_norm
    return (
        left_norm in right_norm
        or right_norm in left_norm
        or len(set(left_norm).intersection(set(right_norm))) >= min(6, len(set(right_norm)))
    )


def average(values: list[float], default: float = 1.0) -> float:
    return sum(values) / len(values) if values else default


def _normalize(value: str) -> str:
    return "".join(ch for ch in value.lower().strip() if not ch.isspace())
