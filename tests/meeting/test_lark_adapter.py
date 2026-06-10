from __future__ import annotations

import json
from pathlib import Path

import pytest

from nanobot.meeting.errors import (
    ApprovalRequiredError,
    ToolExecutionError,
    ToolOperationNotAllowedError,
)
from nanobot.meeting.lark_adapter import CliLarkProvider, CommandResult, LarkToolAdapter, OapiRequest
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


def test_cli_provider_builds_minutes_search_argument_list() -> None:
    seen: list[list[str]] = []

    def runner(argv: list[str], timeout_s: int) -> CommandResult:
        seen.append(argv)
        return CommandResult(argv=argv, exit_code=0, stdout=json.dumps({"data": {"items": []}}), stderr="")

    provider = CliLarkProvider(runner=runner)
    provider.call("minutes.search", {"query": "项目例会", "start": "2026-01-01"}, dry_run=False)

    assert seen
    assert seen[0][:3] == ["lark-cli", "minutes", "+search"]
    assert "--query" in seen[0]
    assert "--start" in seen[0]
    assert "--as" in seen[0]


def test_fake_provider_supports_lifecycle_read_operations(tmp_path: Path) -> None:
    adapter = LarkToolAdapter.fake(workspace=tmp_path)

    agenda = adapter.execute("calendar.agenda", {"query": "项目例会"})
    tasks = adapter.execute("task.search", {"query": "项目"})
    docs = adapter.execute("docs.search", {"query": "项目"})

    assert agenda["items"]
    assert tasks["items"][0]["status"] == "open"
    assert docs["items"][0]["title"]


def test_cli_provider_retries_transient_failures() -> None:
    attempts = 0

    def runner(argv: list[str], timeout_s: int) -> CommandResult:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return CommandResult(argv=argv, exit_code=1, stdout="", stderr="temporary")
        return CommandResult(argv=argv, exit_code=0, stdout=json.dumps({"items": []}), stderr="")

    provider = CliLarkProvider(runner=runner, retry_attempts=2)
    result = provider.call("calendar.agenda", {"query": "项目"}, dry_run=False)

    assert result == {"items": []}
    assert attempts == 2


def test_calendar_write_stays_rejected(tmp_path: Path) -> None:
    adapter = LarkToolAdapter.fake(workspace=tmp_path)

    with pytest.raises(ToolOperationNotAllowedError):
        adapter.execute("calendar.create", {}, dry_run=True)


def test_oapi_provider_maps_read_request_and_passes_token(tmp_path: Path) -> None:
    seen: dict[str, object] = {}

    def runner(*, base_url: str, request: OapiRequest, token: str, timeout_s: int) -> dict:
        seen["base_url"] = base_url
        seen["request"] = request
        seen["token"] = token
        seen["timeout_s"] = timeout_s
        return {"items": []}

    adapter = LarkToolAdapter.oapi(
        workspace=tmp_path,
        access_token="tenant-token",
        base_url="https://open.feishu.cn",
        runner=runner,
    )

    result = adapter.execute("calendar.agenda", {"query": "项目例会", "start": "2026-06-10", "end": "2026-06-11"})

    request = seen["request"]
    assert result == {"items": []}
    assert seen["token"] == "tenant-token"
    assert isinstance(request, OapiRequest)
    assert request.method == "GET"
    assert request.path == "/open-apis/calendar/v4/calendars/primary/events"
    assert request.params["summary"] == "项目例会"
    assert adapter.audit_events[-1].provider_mode == "oapi"


def test_oapi_write_dry_run_returns_preview_without_http(tmp_path: Path) -> None:
    def runner(**kwargs) -> dict:
        raise AssertionError("dry-run write must not call HTTP")

    adapter = LarkToolAdapter.oapi(workspace=tmp_path, access_token="tenant-token", runner=runner)

    result = adapter.execute("docs.create", {"title": "会议纪要", "markdown": "# 内容"}, dry_run=True)

    assert result["dry_run"] is True
    assert result["method"] == "POST"
    assert result["path"] == "/open-apis/docx/v1/documents"
    assert result["json"]["title"] == "会议纪要"


def test_oapi_write_without_approval_is_blocked_before_http(tmp_path: Path) -> None:
    called = False

    def runner(**kwargs) -> dict:
        nonlocal called
        called = True
        return {}

    adapter = LarkToolAdapter.oapi(workspace=tmp_path, access_token="tenant-token", runner=runner)

    with pytest.raises(ApprovalRequiredError):
        adapter.execute("task.create", {"summary": "补充风险清单"}, dry_run=False, approval_status=ApprovalStatus.PENDING)

    assert called is False


def test_oapi_provider_requires_token_for_real_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LARK_OAPI_ACCESS_TOKEN", raising=False)
    adapter = LarkToolAdapter.oapi(workspace=tmp_path, access_token=None)

    status = adapter.execute("auth.status", {})
    assert status["status"] == "missing_token"
    with pytest.raises(ToolExecutionError):
        adapter.execute("vc.search", {"query": "项目例会"})
