from __future__ import annotations

import pytest

from nanobot.meeting.evidence import EvidenceIntegrityValidator
from nanobot.meeting.errors import EvidenceValidationError
from nanobot.meeting.schemas import ActionItem, Decision, EvidenceRef, MeetingMinutes, Risk, TranscriptSegment


def _segment() -> TranscriptSegment:
    return TranscriptSegment(
        segment_id="seg-0001",
        meeting_id="meeting-1",
        speaker_name="Alice",
        start_time="00:01",
        text="Alice 决定先灰度上线。",
    )


def _evidence(segment_id: str = "seg-0001", quote: str = "Alice 决定先灰度上线。") -> EvidenceRef:
    return EvidenceRef(evidence_id="ev-1", meeting_id="meeting-1", segment_id=segment_id, quote=quote)


def test_evidence_validator_accepts_valid_decision_and_action() -> None:
    segment = _segment()
    minutes = MeetingMinutes(
        meeting_id="meeting-1",
        title="项目例会",
        one_sentence_summary="灰度上线",
        detailed_summary=segment.text,
        decisions=[Decision(decision_id="d1", text="先灰度上线", evidence_refs=[_evidence()])],
        action_items=[ActionItem(action_id="a1", task="补充风险清单", evidence_refs=[_evidence()])],
    )

    validated = EvidenceIntegrityValidator().validate_minutes(minutes, [segment])

    assert validated.decisions[0].evidence_refs[0].quote == segment.text
    assert validated.action_items[0].evidence_refs[0].speaker_name == "Alice"


def test_evidence_validator_rejects_unknown_segment_id() -> None:
    segment = _segment()
    minutes = MeetingMinutes(
        meeting_id="meeting-1",
        title="项目例会",
        one_sentence_summary="灰度上线",
        detailed_summary=segment.text,
        decisions=[Decision(decision_id="d1", text="先灰度上线", evidence_refs=[_evidence("seg-missing")])],
    )

    with pytest.raises(EvidenceValidationError):
        EvidenceIntegrityValidator().validate_minutes(minutes, [segment])


def test_evidence_validator_backfills_invented_quote() -> None:
    segment = _segment()
    minutes = MeetingMinutes(
        meeting_id="meeting-1",
        title="项目例会",
        one_sentence_summary="灰度上线",
        detailed_summary=segment.text,
        decisions=[Decision(decision_id="d1", text="先灰度上线", evidence_refs=[_evidence(quote="模型编造的证据")])],
    )

    validated = EvidenceIntegrityValidator().validate_minutes(minutes, [segment])

    assert validated.decisions[0].evidence_refs[0].quote == segment.text


def test_evidence_validator_checks_optional_evidence_when_present() -> None:
    segment = _segment()
    minutes = MeetingMinutes(
        meeting_id="meeting-1",
        title="项目例会",
        one_sentence_summary="风险",
        detailed_summary=segment.text,
        risks=[Risk(risk_id="r1", text="存在延期风险", evidence_refs=[_evidence("seg-missing")])],
    )

    with pytest.raises(EvidenceValidationError):
        EvidenceIntegrityValidator().validate_minutes(minutes, [segment])
