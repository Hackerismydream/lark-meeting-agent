"""Run trace persistence with secret redaction."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any

from nanobot.meeting.schemas import RunTrace, RunTraceEvent


class RunTraceWriter:
    def __init__(self, workspace: Path | str, run_id: str, workflow: str) -> None:
        self.workspace = Path(workspace)
        self.root = self.workspace / ".lark_meeting_agent" / "traces"
        self.trace = RunTrace(run_id=run_id, workflow=workflow)

    def add(self, stage: str, message: str, data: dict[str, Any] | None = None) -> None:
        self.trace.events.append(
            RunTraceEvent(
                event_id=str(uuid.uuid4()),
                stage=stage,
                message=self._redact(message),
                data=self._redact_data(data or {}),
            )
        )

    def save(self) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / f"{self.trace.run_id}.json"
        path.write_text(self.trace.model_dump_json(indent=2))
        return path

    def _redact_data(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {str(k): self._redact_data(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._redact_data(item) for item in value]
        if isinstance(value, str):
            return self._redact(value)
        return value

    @staticmethod
    def _redact(value: str) -> str:
        redacted = re.sub(r"sk-[A-Za-z0-9_\-]+", "[REDACTED]", value)
        redacted = re.sub(r"(?i)(app_secret|access_token|refresh_token|authorization|cookie)=\S+", r"\1=[REDACTED]", redacted)
        redacted = re.sub(r"(?i)Bearer\s+[A-Za-z0-9_.\-]+", "Bearer [REDACTED]", redacted)
        redacted = re.sub(r"https://[^\s]*(?:token|secret|auth)[^\s]*", "https://[REDACTED]", redacted)
        return redacted
