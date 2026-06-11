"""Trace reading and reconstruction helpers."""

from __future__ import annotations

from pathlib import Path

from nanobot.meeting.errors import PersistenceError
from nanobot.meeting.schemas import RunTrace
from nanobot.meeting.trace import RunTraceWriter

__all__ = ["RunTraceWriter", "TraceReader"]


class TraceReader:
    def __init__(self, workspace: Path | str) -> None:
        self.workspace = Path(workspace)
        self.root = self.workspace / ".lark_meeting_agent" / "traces"

    def load(self, run_id: str) -> RunTrace:
        path = self.root / f"{run_id}.json"
        if not path.exists():
            raise PersistenceError(f"trace not found: {run_id}")
        return RunTrace.model_validate_json(path.read_text())
