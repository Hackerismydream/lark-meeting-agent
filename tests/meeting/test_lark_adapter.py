from __future__ import annotations

import json
from pathlib import Path

import pytest

from nanobot.meeting.errors import (
    ApprovalRequiredError,
    ToolExecutionError,
    ToolOperationNotAllowedError,
)
from nanobot.meeting.lark_adapter import CliLarkProvider, CommandResult, LarkToolAdapter
from nanobot.meeting.schemas import ApprovalStatus


def test_fake_provider_searches_fixture_meetings(tmp_path: Path) -> None:
    adapter = LarkToolAdapter.fake(workspace=tmp_path)

    result = adapter.execute("vc.search", {"query": "项目例会"})

    assert result["meetings"][0]["meeting_id"] == "meeting-1"


def test_unknown_operation_is_rejected(tmp_path: Path) -> None:
    adapter = LarkToolAdapter.fake(workspace=tmp_path)

    with pytest.raises(ToolOperationNotAllowedError):
        adapter.execute("drive.delete_file", {})


def test_write_without_approval_is_rejected(tmp_path: Path) -> None:
    adapter = LarkToolAdapter.fake(workspace=tmp_path)

    with pytest.raises(ApprovalRequiredError):
        adapter.execute(
            "docs.create",
            {"title": "会议纪要", "markdown": "# 会议纪要"},
            dry_run=False,
            approval_status=ApprovalStatus.PENDING,
        )


def test_cli_provider_rejects_malformed_json(tmp_path: Path) -> None:
    def runner(argv: list[str], timeout_s: int) -> CommandResult:
        return CommandResult(argv=argv, exit_code=0, stdout="not json", stderr="")

    provider = CliLarkProvider(runner=runner)
    adapter = LarkToolAdapter(provider=provider, workspace=tmp_path)

    with pytest.raises(ToolExecutionError):
        adapter.execute("vc.search", {"query": "项目例会"})


def test_secret_redaction_removes_tokens(tmp_path: Path) -> None:
    adapter = LarkToolAdapter.fake(workspace=tmp_path)

    redacted = adapter.redact("Authorization: Bearer sk-secret app_secret=abc cookie=session")

    assert "sk-secret" not in redacted
    assert "abc" not in redacted
    assert "session" not in redacted
    assert "[REDACTED]" in redacted


def test_cli_provider_builds_argument_lists_not_shell_strings() -> None:
    seen: list[list[str]] = []

    def runner(argv: list[str], timeout_s: int) -> CommandResult:
        seen.append(argv)
        return CommandResult(argv=argv, exit_code=0, stdout=json.dumps({"meetings": []}), stderr="")

    provider = CliLarkProvider(runner=runner)
    provider.call("vc.search", {"query": "项目例会"}, dry_run=False)

    assert seen
    assert seen[0][:3] == ["lark-cli", "vc", "+search"]
    assert "--as" in seen[0]
    assert "user" in seen[0]
    assert all(isinstance(part, str) for part in seen[0])
