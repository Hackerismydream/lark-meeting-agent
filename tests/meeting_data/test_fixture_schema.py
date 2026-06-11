from __future__ import annotations

import pytest
from pydantic import ValidationError

from nanobot.meeting_data.schemas import (
    DatasetName,
    MeetingFixture,
    MeetingMeta,
    MeetingQuery,
    Provenance,
    TranscriptTurn,
)


def valid_fixture() -> MeetingFixture:
    return MeetingFixture(
        fixture_id="qmsum-fixture-1",
        dataset=DatasetName.QMSUM,
        meta=MeetingMeta(title="Test Meeting"),
        provenance=Provenance(source_id="source-1"),
        transcript_turns=[
            TranscriptTurn(turn_id="turn-0001", text="Alice proposes the launch.", speaker="Alice"),
            TranscriptTurn(turn_id="turn-0002", text="Bob owns the checklist.", speaker="Bob"),
        ],
        queries=[
            MeetingQuery(
                query_id="query-001",
                question="Who owns the checklist?",
                relevant_turn_ids=["turn-0002"],
            )
        ],
    )


def test_valid_fixture_accepts_optional_action_and_decision_labels() -> None:
    fixture = valid_fixture()

    assert fixture.expected.action_items == []
    assert fixture.expected.decisions == []


def test_fixture_rejects_empty_transcript_turns() -> None:
    with pytest.raises(ValidationError):
        MeetingFixture(
            fixture_id="bad",
            dataset=DatasetName.QMSUM,
            meta=MeetingMeta(title="Bad"),
            provenance=Provenance(source_id="source"),
            transcript_turns=[],
        )


def test_fixture_rejects_duplicate_turn_ids() -> None:
    with pytest.raises(ValidationError, match="turn_id"):
        MeetingFixture(
            fixture_id="bad",
            dataset=DatasetName.QMSUM,
            meta=MeetingMeta(title="Bad"),
            provenance=Provenance(source_id="source"),
            transcript_turns=[
                TranscriptTurn(turn_id="turn-1", text="one"),
                TranscriptTurn(turn_id="turn-1", text="two"),
            ],
        )


def test_fixture_rejects_query_reference_to_missing_turn() -> None:
    with pytest.raises(ValidationError, match="missing turn ids"):
        MeetingFixture(
            fixture_id="bad",
            dataset=DatasetName.QMSUM,
            meta=MeetingMeta(title="Bad"),
            provenance=Provenance(source_id="source"),
            transcript_turns=[TranscriptTurn(turn_id="turn-1", text="one")],
            queries=[MeetingQuery(query_id="query-1", question="What?", relevant_turn_ids=["missing"])],
        )
