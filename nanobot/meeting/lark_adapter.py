"""Controlled Lark tool boundary."""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nanobot.meeting.errors import (
    ApprovalRequiredError,
    ToolExecutionError,
    ToolOperationNotAllowedError,
)
from nanobot.meeting.schemas import (
    ApprovalStatus,
    ExecutionStatus,
    ProviderMode,
    ReadOrWrite,
    ToolCallAuditEvent,
)

WRITE_OP_NAMES = {"docs.create", "task.create", "im.send", "vc.meeting.join", "vc.meeting.leave"}


@dataclass
class CommandResult:
    argv: list[str]
    exit_code: int
    stdout: str
    stderr: str


@dataclass
class OapiRequest:
    method: str
    path: str
    params: dict[str, Any]
    body: dict[str, Any]


class SubprocessRunner:
    """Small subprocess wrapper that never invokes a shell."""

    def __call__(self, argv: list[str], timeout_s: int) -> CommandResult:
        completed = subprocess.run(
            argv,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return CommandResult(
            argv=argv,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


class FakeLarkProvider:
    mode = ProviderMode.FAKE

    def __init__(self, fixture_root: Path | None = None) -> None:
        self.fixture_root = fixture_root or Path("tests/fixtures/meeting/lark_outputs")

    def call(self, operation: str, payload: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
        if operation == "vc.search":
            return self._read_json("vc_search.json")
        if operation == "vc.notes":
            return self._read_json("vc_notes.json")
        if operation == "minutes.search":
            return {"items": [], "data": {"items": []}}
        if operation == "calendar.agenda":
            return {
                "items": [
                    {
                        "meeting_id": payload.get("meeting_id") or "meeting-1",
                        "title": payload.get("query") or "项目例会",
                        "start_time": payload.get("start") or "2026-06-10T10:00:00+08:00",
                        "end_time": payload.get("end") or "2026-06-10T11:00:00+08:00",
                        "attendees": [{"name": "Alice"}, {"name": "Bob"}],
                    }
                ]
            }
        if operation in {"task.search", "task.list"}:
            return {
                "items": [
                    {
                        "task_id": "task-1",
                        "summary": "补充灰度方案风险清单",
                        "owner": "Alice",
                        "status": "open",
                        "due_date": "2026-06-14",
                    }
                ]
            }
        if operation == "docs.search":
            return {
                "items": [
                    {
                        "doc": "doc-1",
                        "title": "项目背景",
                        "content": "上次会议决定先灰度上线，并补充风险清单。",
                    }
                ]
            }
        if operation == "docs.fetch":
            return {"content": self._read_json("vc_notes.json").get("transcript", "") or "项目背景：先灰度上线。"}
        if operation == "docs.create":
            return {"url": "https://fake.larksuite.com/doc/fake-doc", "token": "fake-doc"}
        if operation == "task.create":
            return {"url": "https://fake.larksuite.com/task/fake-task", "guid": "fake-task"}
        if operation == "im.send":
            return {"message_id": "om_fake", "chat_id": payload.get("chat_id")}
        if operation == "auth.status":
            return {"status": "ok", "provider": "fake"}
        if operation == "vc.meeting.join":
            return {
                "dry_run": dry_run,
                "meeting": {
                    "id": "live-meeting-1",
                    "meeting_number": payload.get("meeting_number") or "123456789",
                    "topic": "项目例会",
                },
            }
        if operation == "vc.meeting.events":
            return {
                "events": [
                    {
                        "event_id": "evt-live-1",
                        "event_type": "transcript_received",
                        "start_time": "00:01",
                        "speaker": {"name": "Alice", "open_id": "ou_alice"},
                        "transcript": {"text": "Alice 决定先灰度上线。"},
                    },
                    {
                        "event_id": "evt-live-2",
                        "event_type": "transcript_received",
                        "start_time": "00:02",
                        "speaker": {"name": "Bob", "open_id": "ou_bob"},
                        "transcript": {"text": "Bob 负责补充风险清单。"},
                    },
                ],
                "has_more": False,
                "page_token": "page-token-1",
            }
        if operation == "vc.meeting.leave":
            return {"status": "left", "meeting_id": payload.get("meeting_id")}
        raise ToolOperationNotAllowedError(f"unknown fake operation: {operation}")

    def _read_json(self, name: str) -> dict[str, Any]:
        path = self.fixture_root / name
        return json.loads(path.read_text())


class CliLarkProvider:
    mode = ProviderMode.CLI

    def __init__(
        self,
        runner: Callable[[list[str], int], CommandResult] | None = None,
        timeout_s: int = 60,
        identity: str = "user",
        retry_attempts: int = 1,
    ) -> None:
        self.runner = runner or SubprocessRunner()
        self.timeout_s = timeout_s
        self.identity = identity
        self.retry_attempts = max(1, retry_attempts)

    def call(self, operation: str, payload: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
        argv = self._argv(operation, payload, dry_run=dry_run)
        last_result: CommandResult | None = None
        for _ in range(self.retry_attempts):
            last_result = self.runner(argv, self.timeout_s)
            if last_result.exit_code == 0:
                break
        result = last_result
        if result is None:
            raise ToolExecutionError("lark-cli did not run")
        if result.exit_code != 0:
            raise ToolExecutionError(result.stderr or f"lark-cli exited {result.exit_code}")
        try:
            parsed = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise ToolExecutionError("lark-cli returned malformed JSON") from exc
        if not isinstance(parsed, dict):
            raise ToolExecutionError("lark-cli JSON output must be an object")
        return parsed

    def _argv(self, operation: str, payload: dict[str, Any], *, dry_run: bool) -> list[str]:
        common = ["--format", "json", "--as", self.identity]
        if dry_run:
            common.append("--dry-run")
        if operation == "auth.status":
            return ["lark-cli", "auth", "status"]
        if operation == "vc.search":
            argv = ["lark-cli", "vc", "+search", *common]
            if query := payload.get("query"):
                argv.extend(["--query", str(query)])
            if start := payload.get("start"):
                argv.extend(["--start", str(start)])
            if end := payload.get("end"):
                argv.extend(["--end", str(end)])
            return argv
        if operation == "vc.notes":
            argv = ["lark-cli", "vc", "+notes", *common]
            self._add_any(argv, payload, "meeting_id", "--meeting-ids")
            self._add_any(argv, payload, "minute_token", "--minute-tokens")
            self._add_any(argv, payload, "calendar_event_id", "--calendar-event-ids")
            return argv
        if operation == "vc.meeting.join":
            meeting_number = payload.get("meeting_number")
            if not meeting_number:
                raise ToolExecutionError("meeting_number is required for vc.meeting.join")
            argv = ["lark-cli", "vc", "+meeting-join", *common, "--meeting-number", str(meeting_number)]
            if password := payload.get("password"):
                argv.extend(["--password", str(password)])
            return argv
        if operation == "vc.meeting.events":
            meeting_id = payload.get("meeting_id")
            if not meeting_id:
                raise ToolExecutionError("meeting_id is required for vc.meeting.events")
            argv = ["lark-cli", "vc", "+meeting-events", *common, "--meeting-id", str(meeting_id)]
            if start := payload.get("start"):
                argv.extend(["--start", str(start)])
            if end := payload.get("end"):
                argv.extend(["--end", str(end)])
            if page_token := payload.get("page_token"):
                argv.extend(["--page-token", str(page_token)])
            if page_size := payload.get("page_size"):
                argv.extend(["--page-size", str(page_size)])
            if payload.get("page_all", True):
                argv.append("--page-all")
            return argv
        if operation == "vc.meeting.leave":
            meeting_id = payload.get("meeting_id")
            if not meeting_id:
                raise ToolExecutionError("meeting_id is required for vc.meeting.leave")
            return ["lark-cli", "vc", "+meeting-leave", *common, "--meeting-id", str(meeting_id)]
        if operation == "minutes.search":
            argv = ["lark-cli", "minutes", "+search", *common]
            if query := payload.get("query"):
                argv.extend(["--query", str(query)])
            if owner_ids := payload.get("owner_ids"):
                argv.extend(["--owner-ids", str(owner_ids)])
            if participant_ids := payload.get("participant_ids"):
                argv.extend(["--participant-ids", str(participant_ids)])
            if start := payload.get("start"):
                argv.extend(["--start", str(start)])
            if end := payload.get("end"):
                argv.extend(["--end", str(end)])
            return argv
        if operation == "calendar.agenda":
            argv = ["lark-cli", "calendar", "+agenda", *common]
            if query := payload.get("query"):
                argv.extend(["--query", str(query)])
            if start := payload.get("start"):
                argv.extend(["--start", str(start)])
            if end := payload.get("end"):
                argv.extend(["--end", str(end)])
            return argv
        if operation in {"task.search", "task.list"}:
            argv = ["lark-cli", "task", "+list", *common]
            if query := payload.get("query"):
                argv.extend(["--query", str(query)])
            if status := payload.get("status"):
                argv.extend(["--status", str(status)])
            return argv
        if operation == "docs.search":
            argv = ["lark-cli", "docs", "+search", "--api-version", "v2", *common]
            if query := payload.get("query"):
                argv.extend(["--query", str(query)])
            return argv
        if operation == "docs.fetch":
            return [
                "lark-cli",
                "docs",
                "+fetch",
                "--api-version",
                "v2",
                *common,
                "--doc",
                str(payload.get("doc") or payload.get("token") or ""),
            ]
        if operation == "docs.create":
            return [
                "lark-cli",
                "docs",
                "+create",
                "--api-version",
                "v2",
                *common,
                "--title",
                str(payload.get("title") or "会议纪要"),
                "--markdown",
                str(payload.get("markdown") or ""),
            ]
        if operation == "task.create":
            argv = [
                "lark-cli",
                "task",
                "+create",
                *common,
                "--summary",
                str(payload.get("summary") or "会议待办"),
                "--description",
                str(payload.get("description") or ""),
            ]
            if due := payload.get("due"):
                argv.extend(["--due", str(due)])
            if assignee := payload.get("assignee"):
                argv.extend(["--assignee", str(assignee)])
            return argv
        if operation == "im.send":
            chat_id = payload.get("chat_id")
            if not chat_id:
                raise ToolExecutionError("chat_id is required for im.send")
            return [
                "lark-cli",
                "im",
                "+messages-send",
                *common,
                "--chat-id",
                str(chat_id),
                "--markdown",
                str(payload.get("markdown") or payload.get("text") or ""),
            ]
        raise ToolOperationNotAllowedError(f"operation not allowlisted: {operation}")

    @staticmethod
    def _add_any(argv: list[str], payload: dict[str, Any], key: str, flag: str) -> None:
        if value := payload.get(key):
            argv.extend([flag, str(value)])


class OapiHttpRunner:
    """Small HTTP runner for Lark OpenAPI requests."""

    def __call__(
        self,
        *,
        base_url: str,
        request: OapiRequest,
        token: str,
        timeout_s: int,
    ) -> dict[str, Any]:
        query = urllib.parse.urlencode({key: value for key, value in request.params.items() if value is not None})
        url = f"{base_url.rstrip('/')}{request.path}"
        if query:
            url = f"{url}?{query}"
        data = json.dumps(request.body, ensure_ascii=False).encode("utf-8") if request.body else None
        http_request = urllib.request.Request(
            url,
            data=data,
            method=request.method,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        try:
            with urllib.request.urlopen(http_request, timeout=timeout_s) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ToolExecutionError(f"Lark OpenAPI HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise ToolExecutionError(f"Lark OpenAPI request failed: {exc.reason}") from exc
        try:
            parsed = json.loads(payload or "{}")
        except json.JSONDecodeError as exc:
            raise ToolExecutionError("Lark OpenAPI returned malformed JSON") from exc
        if not isinstance(parsed, dict):
            raise ToolExecutionError("Lark OpenAPI JSON output must be an object")
        return parsed


class OapiLarkProvider:
    mode = ProviderMode.OAPI

    def __init__(
        self,
        *,
        access_token: str | None = None,
        base_url: str = "https://open.feishu.cn",
        runner: Callable[..., dict[str, Any]] | None = None,
        timeout_s: int = 30,
    ) -> None:
        self.access_token = access_token or os.environ.get("LARK_OAPI_ACCESS_TOKEN")
        self.base_url = base_url
        self.runner = runner or OapiHttpRunner()
        self.timeout_s = timeout_s

    def call(self, operation: str, payload: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
        if operation == "auth.status":
            return {
                "status": "configured" if self.access_token else "missing_token",
                "provider": "oapi",
                "base_url": self.base_url,
            }
        request = self._request(operation, payload)
        if dry_run and operation in WRITE_OP_NAMES:
            return {
                "dry_run": True,
                "provider": "oapi",
                "method": request.method,
                "path": request.path,
                "params": request.params,
                "json": request.body,
            }
        if not self.access_token:
            raise ToolExecutionError("LARK_OAPI_ACCESS_TOKEN is required for OAPI provider")
        return self.runner(base_url=self.base_url, request=request, token=self.access_token, timeout_s=self.timeout_s)

    def _request(self, operation: str, payload: dict[str, Any]) -> OapiRequest:
        if operation == "calendar.agenda":
            return OapiRequest(
                method="GET",
                path="/open-apis/calendar/v4/calendars/primary/events",
                params={
                    "start_time": payload.get("start"),
                    "end_time": payload.get("end"),
                    "summary": payload.get("query"),
                },
                body={},
            )
        if operation == "vc.search":
            return OapiRequest(
                method="GET",
                path="/open-apis/vc/v1/meetings",
                params={"query": payload.get("query"), "start_time": payload.get("start"), "end_time": payload.get("end")},
                body={},
            )
        if operation == "vc.notes":
            meeting_id = payload.get("meeting_id") or payload.get("minute_token") or ""
            return OapiRequest(
                method="GET",
                path=f"/open-apis/vc/v1/meetings/{urllib.parse.quote(str(meeting_id), safe='')}/notes",
                params={},
                body={},
            )
        if operation == "vc.meeting.join":
            return OapiRequest(
                method="POST",
                path="/open-apis/vc/v1/bots/join",
                params={},
                body={
                    "meeting_number": payload.get("meeting_number"),
                    **({"password": payload["password"]} if payload.get("password") else {}),
                },
            )
        if operation == "vc.meeting.events":
            return OapiRequest(
                method="GET",
                path="/open-apis/vc/v1/bots/events",
                params={
                    "meeting_id": payload.get("meeting_id"),
                    "start_time": payload.get("start"),
                    "end_time": payload.get("end"),
                    "page_token": payload.get("page_token"),
                    "page_size": payload.get("page_size"),
                },
                body={},
            )
        if operation == "vc.meeting.leave":
            return OapiRequest(
                method="POST",
                path="/open-apis/vc/v1/bots/leave",
                params={},
                body={"meeting_id": payload.get("meeting_id")},
            )
        if operation == "minutes.search":
            return OapiRequest(
                method="GET",
                path="/open-apis/minutes/v1/minutes",
                params={
                    "query": payload.get("query"),
                    "start_time": payload.get("start"),
                    "end_time": payload.get("end"),
                    "owner_ids": payload.get("owner_ids"),
                    "participant_ids": payload.get("participant_ids"),
                },
                body={},
            )
        if operation == "docs.search":
            return OapiRequest(
                method="GET",
                path="/open-apis/search/v2/data_search",
                params={"query": payload.get("query"), "data_types": "doc,docx"},
                body={},
            )
        if operation == "docs.fetch":
            doc = payload.get("doc") or payload.get("token") or ""
            return OapiRequest(
                method="GET",
                path=f"/open-apis/docx/v1/documents/{urllib.parse.quote(str(doc), safe='')}/raw_content",
                params={},
                body={},
            )
        if operation in {"task.search", "task.list"}:
            return OapiRequest(
                method="GET",
                path="/open-apis/task/v2/tasks",
                params={"summary": payload.get("query"), "status": payload.get("status")},
                body={},
            )
        if operation == "docs.create":
            return OapiRequest(
                method="POST",
                path="/open-apis/docx/v1/documents",
                params={},
                body={"title": payload.get("title") or "会议纪要", "content": payload.get("markdown") or ""},
            )
        if operation == "task.create":
            body = {
                "summary": payload.get("summary") or "会议待办",
                "description": payload.get("description") or "",
            }
            if due := payload.get("due"):
                body["due"] = due
            if assignee := payload.get("assignee"):
                body["assignee"] = assignee
            return OapiRequest(method="POST", path="/open-apis/task/v2/tasks", params={}, body=body)
        if operation == "im.send":
            chat_id = payload.get("chat_id")
            if not chat_id:
                raise ToolExecutionError("chat_id is required for im.send")
            content = {"text": payload.get("markdown") or payload.get("text") or ""}
            return OapiRequest(
                method="POST",
                path="/open-apis/im/v1/messages",
                params={"receive_id_type": "chat_id"},
                body={"receive_id": chat_id, "msg_type": "text", "content": json.dumps(content, ensure_ascii=False)},
            )
        raise ToolOperationNotAllowedError(f"operation not allowlisted: {operation}")


class LarkToolAdapter:
    READ_OPS = {
        "auth.status",
        "vc.search",
        "vc.notes",
        "vc.meeting.events",
        "docs.fetch",
        "docs.search",
        "minutes.search",
        "calendar.agenda",
        "task.search",
        "task.list",
    }
    WRITE_OPS = WRITE_OP_NAMES

    def __init__(self, provider: FakeLarkProvider | CliLarkProvider | OapiLarkProvider, workspace: Path | str) -> None:
        self.provider = provider
        self.workspace = Path(workspace)
        self.audit_events: list[ToolCallAuditEvent] = []

    @classmethod
    def fake(cls, workspace: Path | str) -> "LarkToolAdapter":
        return cls(FakeLarkProvider(), workspace)

    @classmethod
    def cli(cls, workspace: Path | str) -> "LarkToolAdapter":
        return cls(CliLarkProvider(), workspace)

    @classmethod
    def oapi(
        cls,
        workspace: Path | str,
        *,
        access_token: str | None = None,
        base_url: str = "https://open.feishu.cn",
        runner: Callable[..., dict[str, Any]] | None = None,
    ) -> "LarkToolAdapter":
        return cls(OapiLarkProvider(access_token=access_token, base_url=base_url, runner=runner), workspace)

    def execute(
        self,
        operation: str,
        payload: dict[str, Any],
        *,
        dry_run: bool = False,
        approval_status: ApprovalStatus | str | None = None,
    ) -> dict[str, Any]:
        read_or_write = self._classify(operation)
        approval = ApprovalStatus(approval_status) if isinstance(approval_status, str) else approval_status
        if read_or_write == ReadOrWrite.WRITE and not dry_run and approval != ApprovalStatus.APPROVED:
            self._audit(operation, payload, read_or_write, dry_run, approval, ExecutionStatus.FAILED, "approval required")
            raise ApprovalRequiredError(f"{operation} requires approval")
        try:
            result = self.provider.call(operation, payload, dry_run=dry_run)
        except Exception as exc:
            self._audit(operation, payload, read_or_write, dry_run, approval, ExecutionStatus.FAILED, str(exc))
            raise
        status = ExecutionStatus.DRY_RUN if dry_run and read_or_write == ReadOrWrite.WRITE else ExecutionStatus.COMPLETED
        self._audit(operation, payload, read_or_write, dry_run, approval, status, None, result)
        return result

    def redact(self, value: str) -> str:
        redacted = re.sub(r"sk-[A-Za-z0-9_\-]+", "[REDACTED]", value)
        redacted = re.sub(
            r"(?i)(app_secret|access_token|refresh_token|authorization|cookie|password|passcode|meeting_password)=\S+",
            r"\1=[REDACTED]",
            redacted,
        )
        redacted = re.sub(
            r'(?i)"(password|passcode|meeting_password)"\s*:\s*"[^"]*"',
            r'"\1": "[REDACTED]"',
            redacted,
        )
        redacted = re.sub(r"(?i)Bearer\s+\S+", "Bearer [REDACTED]", redacted)
        return redacted

    def _classify(self, operation: str) -> ReadOrWrite:
        if operation in self.READ_OPS:
            return ReadOrWrite.READ
        if operation in self.WRITE_OPS:
            return ReadOrWrite.WRITE
        raise ToolOperationNotAllowedError(f"operation not allowlisted: {operation}")

    def _audit(
        self,
        operation: str,
        payload: dict[str, Any],
        read_or_write: ReadOrWrite,
        dry_run: bool,
        approval_status: ApprovalStatus | None,
        execution_status: ExecutionStatus,
        error_message: str | None = None,
        result: dict[str, Any] | None = None,
    ) -> None:
        sanitized = json.loads(self.redact(json.dumps(payload, ensure_ascii=False, default=str)))
        self.audit_events.append(
            ToolCallAuditEvent(
                audit_id=str(uuid.uuid4()),
                operation_name=operation,
                provider_mode=self.provider.mode,
                sanitized_input=sanitized,
                read_or_write=read_or_write,
                dry_run=dry_run,
                approval_status=approval_status,
                execution_status=execution_status,
                result_summary=self.redact(json.dumps(result, ensure_ascii=False, default=str))[:500]
                if result
                else None,
                error_message=self.redact(error_message) if error_message else None,
            )
        )
