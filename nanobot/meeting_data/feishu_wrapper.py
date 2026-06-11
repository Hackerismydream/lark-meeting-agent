"""Convert public meeting fixtures into Feishu-like contexts."""

from __future__ import annotations

from nanobot.meeting_data.schemas import (
    FeishuLikeMeetingContext,
    MeetingFixture,
    MockAgendaDoc,
    MockCalendarEvent,
    MockOutputTargets,
    MockParticipant,
)
from nanobot.meeting_data.streaming import build_transcript_chunks


def fixture_to_feishu_context(fixture: MeetingFixture) -> FeishuLikeMeetingContext:
    participants = _participants(fixture)
    event = MockCalendarEvent(
        event_id=f"evt-{fixture.fixture_id}",
        title=fixture.meta.title,
        start_time=fixture.meta.date,
        organizer=participants[0].name if participants else None,
        participant_ids=[participant.participant_id for participant in participants],
    )
    agenda_doc = MockAgendaDoc(
        doc_id=f"agenda-{fixture.fixture_id}",
        title=f"{fixture.meta.title} agenda",
        markdown=_agenda_markdown(fixture),
        source_agenda_ids=[item.agenda_id for item in fixture.agenda],
    )
    chunks = fixture.transcript_chunks or build_transcript_chunks(fixture.transcript_turns)
    return FeishuLikeMeetingContext(
        fixture_id=fixture.fixture_id,
        calendar_event=event,
        agenda_doc=agenda_doc,
        participants=participants,
        transcript_stream=chunks,
        meeting_chat_events=_chat_events(fixture),
        related_docs=_related_docs(fixture),
        output_targets=MockOutputTargets(
            docs_folder_token=f"sandbox-docs-{fixture.dataset.value}",
            task_list_guid=f"sandbox-tasks-{fixture.dataset.value}",
            chat_id=f"sandbox-chat-{fixture.dataset.value}",
            sandbox_only=True,
        ),
        approval_policy="dry_run_required",
    )


def _participants(fixture: MeetingFixture) -> list[MockParticipant]:
    names: list[str] = []
    for turn in fixture.transcript_turns:
        if turn.speaker and turn.speaker not in names:
            names.append(turn.speaker)
    if not names:
        names = ["Unknown Speaker"]
    return [
        MockParticipant(participant_id=f"p-{index + 1:03d}", name=name)
        for index, name in enumerate(names[:20])
    ]


def _agenda_markdown(fixture: MeetingFixture) -> str:
    if not fixture.agenda:
        return f"# {fixture.meta.title}\n\nNo source agenda was provided."
    lines = [f"# {fixture.meta.title}", ""]
    for item in fixture.agenda:
        lines.append(f"- **{item.title}**")
        if item.summary:
            lines.append(f"  - {item.summary}")
    return "\n".join(lines)


def _chat_events(fixture: MeetingFixture) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    for query in fixture.queries[:3]:
        events.append(
            {
                "event_id": f"chat-{query.query_id}",
                "sender": "meeting-agent-evaluator",
                "text": query.question,
            }
        )
    return events


def _related_docs(fixture: MeetingFixture) -> list[dict[str, str]]:
    docs = [
        {
            "doc_id": f"provenance-{fixture.fixture_id}",
            "title": f"Dataset provenance: {fixture.dataset.value}",
            "content": fixture.provenance.model_dump_json(),
        }
    ]
    if fixture.expected.overall_summary:
        docs.append(
            {
                "doc_id": f"reference-summary-{fixture.fixture_id}",
                "title": "Reference summary",
                "content": fixture.expected.overall_summary,
            }
        )
    return docs
