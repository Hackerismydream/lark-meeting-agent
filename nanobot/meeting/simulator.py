"""Fixture-backed live meeting simulator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import Field

from nanobot.meeting.schemas import MeetingBaseModel


class ScenarioParticipant(MeetingBaseModel):
    participant_id: str
    display_name: str
    role: str = "participant"
    org: str | None = None
    is_external: bool = False


class ScenarioAgendaItem(MeetingBaseModel):
    title: str
    owner: str | None = None


class ScenarioMemorySeed(MeetingBaseModel):
    project: str | None = None
    customer: str | None = None
    facts: list[str] = Field(default_factory=list)
    open_actions: list[str] = Field(default_factory=list)


class SimulatedMeetingEvent(MeetingBaseModel):
    event_id: str | None = None
    event_type: str
    ts_ms: int = 0
    speaker_id: str | None = None
    speaker_name: str | None = None
    text: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    segment_id: str | None = None

    def to_lark_event(self) -> dict[str, Any]:
        payload = dict(self.payload)
        event: dict[str, Any] = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": _timestamp(self.ts_ms),
            "tags": self.tags,
            **payload,
        }
        if self.speaker_name:
            key = "sender" if self.event_type == "chat_received" else "speaker"
            event[key] = {"name": self.speaker_name, **({"open_id": self.speaker_id} if self.speaker_id else {})}
        if self.segment_id:
            event["segment_id"] = self.segment_id
        if self.text:
            if self.event_type == "transcript_received":
                event["transcript"] = {"text": self.text}
            elif self.event_type == "chat_received":
                event["message"] = {"text": self.text}
            else:
                event["text"] = self.text
        return {key: value for key, value in event.items() if value is not None}


class ExpectedQA(MeetingBaseModel):
    question: str
    expected_segment_ids: list[str] = Field(default_factory=list)
    ask_after_event_id: str | None = None


class SafetyExpectation(MeetingBaseModel):
    case_id: str
    text: str
    forbidden_operation: str | None = None


class ScenarioExpectedOutcomes(MeetingBaseModel):
    decisions: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    qa_cases: list[ExpectedQA] = Field(default_factory=list)
    safety_cases: list[SafetyExpectation] = Field(default_factory=list)


class MeetingScenario(MeetingBaseModel):
    scenario_id: str
    title: str
    meeting_type: str
    project: str | None = None
    customer: str | None = None
    participants: list[ScenarioParticipant] = Field(default_factory=list)
    agenda: list[ScenarioAgendaItem] = Field(default_factory=list)
    memory_seed: ScenarioMemorySeed = Field(default_factory=ScenarioMemorySeed)
    timeline: list[SimulatedMeetingEvent] = Field(default_factory=list)
    expected: ScenarioExpectedOutcomes = Field(default_factory=ScenarioExpectedOutcomes)

    @property
    def transcript_text(self) -> str:
        rows = []
        for event in self.timeline:
            if event.event_type in {"transcript_received", "chat_received"} and event.text:
                speaker = event.speaker_name or "Unknown"
                rows.append(f"[{_timestamp(event.ts_ms)}] {speaker}: {event.text}")
        return "\n".join(rows)


class SimulatedEventPage(MeetingBaseModel):
    events: list[dict[str, Any]] = Field(default_factory=list)
    has_more: bool = False
    page_token: str | None = None
    next_page_token: str | None = None


class LiveMeetingSimulator:
    def __init__(self, scenario: MeetingScenario) -> None:
        self.scenario = scenario

    @classmethod
    def from_dir(cls, path: Path | str) -> "LiveMeetingSimulator":
        return cls(load_scenario(path))

    def page(self, *, page_size: int = 100, page_token: str | None = None) -> SimulatedEventPage:
        start = _decode_page_token(page_token)
        end = min(start + max(1, page_size), len(self.scenario.timeline))
        events = [event.to_lark_event() for event in self.scenario.timeline[start:end]]
        has_more = end < len(self.scenario.timeline)
        next_token = _encode_page_token(end) if has_more else None
        return SimulatedEventPage(
            events=events,
            has_more=has_more,
            page_token=page_token,
            next_page_token=next_token,
        )

    def pages(self, *, page_size: int = 100) -> list[SimulatedEventPage]:
        pages: list[SimulatedEventPage] = []
        token: str | None = None
        while True:
            page = self.page(page_size=page_size, page_token=token)
            pages.append(page)
            if not page.has_more:
                return pages
            token = page.next_page_token


def load_scenarios(root: Path | str) -> list[MeetingScenario]:
    return [load_scenario(path) for path in sorted(Path(root).iterdir()) if path.is_dir()]


def load_scenario(path: Path | str) -> MeetingScenario:
    root = Path(path)
    scenario_data = _read_json(root / "scenario.json")
    timeline = [SimulatedMeetingEvent.model_validate(row) for row in _read_jsonl(root / "timeline.jsonl")]
    expected = ScenarioExpectedOutcomes.model_validate(_read_json(root / "expected.json"))
    participants = [ScenarioParticipant.model_validate(item) for item in scenario_data.get("participants", [])]
    agenda = [ScenarioAgendaItem.model_validate(item) for item in scenario_data.get("agenda", [])]
    memory_seed = ScenarioMemorySeed.model_validate(_read_json(root / "memory_seed.json"))
    return MeetingScenario(
        scenario_id=str(scenario_data["scenario_id"]),
        title=str(scenario_data["title"]),
        meeting_type=str(scenario_data["meeting_type"]),
        project=scenario_data.get("project"),
        customer=scenario_data.get("customer"),
        participants=participants,
        agenda=agenda,
        memory_seed=memory_seed,
        timeline=timeline,
        expected=expected,
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _encode_page_token(offset: int) -> str:
    return f"offset:{offset}"


def _decode_page_token(token: str | None) -> int:
    if not token:
        return 0
    if token.startswith("offset:"):
        return max(0, int(token.split(":", 1)[1]))
    return 0


def _timestamp(ts_ms: int) -> str:
    total_seconds = max(0, ts_ms // 1000)
    minutes, seconds = divmod(total_seconds, 60)
    return f"00:{minutes:02d}:{seconds:02d}"
