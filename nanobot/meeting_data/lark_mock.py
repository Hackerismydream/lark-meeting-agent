"""Local mock Lark tools for meeting-data evaluation."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nanobot.meeting_data.schemas import FeishuLikeMeetingContext, MeetingFixture


class MockLarkTools:
    """Mock Feishu/Lark chain that writes only local artifacts."""

    def __init__(self, output_root: Path | str, run_id: str | None = None) -> None:
        self.run_id = run_id or str(uuid.uuid4())
        self.root = Path(output_root) / self.run_id
        self.artifact_dir = self.root / "artifacts"
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.trace_path = self.root / "trace.jsonl"

    def get_calendar_event(self, context: FeishuLikeMeetingContext) -> dict[str, Any]:
        return self._tool("get_calendar_event", context.calendar_event.model_dump(mode="json"))

    def get_agenda_doc(self, context: FeishuLikeMeetingContext) -> dict[str, Any] | None:
        if not context.agenda_doc:
            return None
        return self._tool("get_agenda_doc", context.agenda_doc.model_dump(mode="json"))

    def stream_transcript(self, context: FeishuLikeMeetingContext) -> list[dict[str, Any]]:
        chunks = [chunk.model_dump(mode="json") for chunk in context.transcript_stream]
        return self._tool("stream_transcript", {"chunks": chunks})["chunks"]

    def create_minutes_doc(self, fixture: MeetingFixture) -> Path:
        self._trace("tool_call_started", "create_minutes_doc", {"fixture_id": fixture.fixture_id})
        path = self.artifact_dir / "minutes.md"
        summary = fixture.expected.overall_summary or "\n".join(chunk.text for chunk in fixture.transcript_chunks[:2])
        path.write_text(f"# {fixture.meta.title}\n\n{summary}\n", encoding="utf-8")
        self._trace("artifact_created", "minutes.md", {"path": str(path)})
        self._trace("tool_call_succeeded", "create_minutes_doc", {"path": str(path)})
        return path

    def create_action_items(self, fixture: MeetingFixture) -> Path:
        self._trace("tool_call_started", "create_action_items", {"fixture_id": fixture.fixture_id})
        path = self.artifact_dir / "action_items.json"
        items = [item.model_dump(mode="json") for item in fixture.expected.action_items]
        path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        self._trace("artifact_created", "action_items.json", {"path": str(path), "count": len(items)})
        self._trace("tool_call_succeeded", "create_action_items", {"path": str(path)})
        return path

    def create_decision_log(self, fixture: MeetingFixture) -> Path:
        self._trace("tool_call_started", "create_decision_log", {"fixture_id": fixture.fixture_id})
        path = self.artifact_dir / "decisions.json"
        decisions = [item.model_dump(mode="json") for item in fixture.expected.decisions]
        path.write_text(json.dumps(decisions, ensure_ascii=False, indent=2), encoding="utf-8")
        self._trace("artifact_created", "decisions.json", {"path": str(path), "count": len(decisions)})
        self._trace("tool_call_succeeded", "create_decision_log", {"path": str(path)})
        return path

    def send_follow_up_message(self, fixture: MeetingFixture) -> Path:
        self._trace("tool_call_started", "send_follow_up_message", {"fixture_id": fixture.fixture_id})
        path = self.artifact_dir / "follow_up_message.md"
        path.write_text(
            f"已生成 {fixture.meta.title} 的会议产物。来源数据集：{fixture.dataset.value}。\n",
            encoding="utf-8",
        )
        self._trace("artifact_created", "follow_up_message.md", {"path": str(path)})
        self._trace("tool_call_succeeded", "send_follow_up_message", {"path": str(path)})
        return path

    def write_report(self, payload: dict[str, Any]) -> Path:
        path = self.root / "report.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self._trace("eval_observation", "report_written", {"path": str(path)})
        return path

    def evidence_linked(self, payload: dict[str, Any]) -> None:
        self._trace("evidence_linked", "evidence linked", payload)

    def _tool(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._trace("tool_call_started", name, {"payload_keys": sorted(payload)})
        self._trace("tool_call_succeeded", name, {"payload_keys": sorted(payload)})
        return payload

    def _trace(self, event_type: str, message: str, data: dict[str, Any]) -> None:
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "event_type": event_type,
            "message": message,
            "data": data,
        }
        with self.trace_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
