from __future__ import annotations

import json
from pathlib import Path

from nanobot.meeting.cli import main as meeting_cli_main
from nanobot.meeting.errors import ToolExecutionError
from nanobot.meeting.transcript_gate import TranscriptGateWorkflow


class GateFakeAdapter:
    def __init__(self, payloads: dict[str, dict]) -> None:
        self.payloads = payloads
        self.calls: list[tuple[str, dict, bool]] = []

    def execute(self, operation: str, payload: dict, *, dry_run: bool = False, **kwargs) -> dict:
        self.calls.append((operation, payload, dry_run))
        if operation == "vc.notes":
            meeting_id = payload.get("meeting_id")
            if isinstance(self.payloads.get(f"vc.notes:{meeting_id}"), Exception):
                raise self.payloads[f"vc.notes:{meeting_id}"]
            return self.payloads.get(f"vc.notes:{meeting_id}", {})
        return self.payloads.get(operation, {})


def test_transcript_gate_reports_ready_when_meeting_notes_have_transcript(tmp_path: Path) -> None:
    adapter = GateFakeAdapter(
        {
            "auth.status": {"status": "ok"},
            "vc.search": {"meetings": [{"meeting_id": "meeting-1", "title": "项目例会"}]},
            "vc.notes:meeting-1": {"transcript": "张三: 我们决定本周灰度上线。"},
            "minutes.search": {"items": []},
        }
    )

    report = TranscriptGateWorkflow(tmp_path, adapter_factory=lambda mode: adapter).run(query="项目例会", provider_mode="cli")

    assert report.status == "ready"
    assert report.visible_meeting_count == 1
    assert report.readable_source is not None
    assert report.readable_source.meeting_id == "meeting-1"
    assert "scripts/lma-real process" in report.next_process_command
    assert all(call[0] in {"auth.status", "vc.search", "vc.notes", "minutes.search"} for call in adapter.calls)


def test_transcript_gate_reports_blocked_with_checked_reasons(tmp_path: Path) -> None:
    adapter = GateFakeAdapter(
        {
            "auth.status": {"status": "ok"},
            "vc.search": {"meetings": [{"meeting_id": "meeting-1", "title": "无纪要会议"}]},
            "vc.notes:meeting-1": {"error": "no notes available for this meeting"},
            "minutes.search": {"items": []},
        }
    )

    report = TranscriptGateWorkflow(tmp_path, adapter_factory=lambda mode: adapter).run(query="无纪要", provider_mode="cli")

    assert report.status == "blocked"
    assert report.checked_meetings[0].meeting_id == "meeting-1"
    assert "no notes available" in report.checked_meetings[0].reason
    assert "没有找到可读取" in report.blocker_message
    assert report.next_process_command is None


def test_transcript_gate_records_notes_errors_without_crashing(tmp_path: Path) -> None:
    adapter = GateFakeAdapter(
        {
            "auth.status": {"status": "ok"},
            "vc.search": {"meetings": [{"meeting_id": "meeting-1", "title": "权限不足会议"}]},
            "vc.notes:meeting-1": ToolExecutionError("all 1 queries failed"),
            "minutes.search": {"items": []},
        }
    )

    report = TranscriptGateWorkflow(Path("."), adapter_factory=lambda mode: adapter).run(provider_mode="cli")

    assert report.status == "blocked"
    assert report.checked_meetings[0].meeting_id == "meeting-1"
    assert "all 1 queries failed" in report.checked_meetings[0].reason


def test_transcript_gate_summarizes_cli_json_error_message(tmp_path: Path) -> None:
    adapter = GateFakeAdapter(
        {
            "auth.status": {"status": "ok"},
            "vc.search": {"meetings": [{"meeting_id": "meeting-1", "title": "权限不足会议"}]},
            "vc.notes:meeting-1": ToolExecutionError(
                '[vc +notes] failed\n{"ok": false, "error": {"type": "api_error", "message": "all 1 queries failed"}}'
            ),
            "minutes.search": {"items": []},
        }
    )

    report = TranscriptGateWorkflow(Path("."), adapter_factory=lambda mode: adapter).run(provider_mode="cli")

    assert report.checked_meetings[0].reason == "all 1 queries failed"


def test_transcript_gate_cli_outputs_json(tmp_path: Path, capsys) -> None:
    exit_code = meeting_cli_main(
        [
            "--workspace",
            str(tmp_path),
            "transcript-gate",
            "--query",
            "项目例会",
            "--provider-mode",
            "fake",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] in {"ready", "blocked"}
    assert payload["provider_mode"] == "fake"
