"""Transcript-grounded evidence validation."""

from __future__ import annotations

from collections.abc import Iterable

from nanobot.meeting.errors import EvidenceValidationError
from nanobot.meeting.schemas import EvidenceRef, MeetingMinutes, TranscriptSegment


class EvidenceIntegrityValidator:
    """Validate and normalize evidence refs against transcript segments."""

    def validate_minutes(self, minutes: MeetingMinutes, segments: list[TranscriptSegment]) -> MeetingMinutes:
        segment_index = {segment.segment_id: segment for segment in segments}
        validated = minutes.model_copy(deep=True)
        for decision in validated.decisions:
            self._validate_refs(decision.evidence_refs, segment_index, f"decision {decision.decision_id}")
        for action in validated.action_items:
            self._validate_refs(action.evidence_refs, segment_index, f"action item {action.action_id}")
        for risk in validated.risks:
            self._validate_refs(risk.evidence_refs, segment_index, f"risk {risk.risk_id}")
        for question in validated.open_questions:
            self._validate_refs(question.evidence_refs, segment_index, f"open question {question.question_id}")
        for chapter in validated.chapters:
            self._validate_refs(chapter.evidence_refs, segment_index, f"chapter {chapter.title}")
        return validated

    def _validate_refs(
        self,
        refs: Iterable[EvidenceRef],
        segment_index: dict[str, TranscriptSegment],
        owner: str,
    ) -> None:
        for ref in refs:
            segment = segment_index.get(ref.segment_id)
            if segment is None:
                raise EvidenceValidationError(f"{owner} references unknown segment_id: {ref.segment_id}")
            ref.meeting_id = segment.meeting_id
            if ref.quote not in segment.text:
                ref.quote = segment.text
            if not ref.speaker_name:
                ref.speaker_name = segment.speaker_name
            if not ref.timestamp:
                ref.timestamp = segment.start_time
