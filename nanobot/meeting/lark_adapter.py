"""Controlled Lark tool boundary."""

from __future__ import annotations

import json
import re
import subprocess
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


@dataclass
class CommandResult:
    argv: list[str]
    exit_code: int
    stdout: str
    stderr: str


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
        if operation == "docs.fetch":
            return {"content": self._read_json("vc_notes.json").get("transcript", "")}
        if operation == "docs.create":
            return {"url": "https://fake.larksuite.com/doc/fake-doc", "token": "fake-doc"}
        if operation == "task.create":
            return {"url": "https://fake.larksuite.com/task/fake-task", "guid": "fake-task"}
        if operation == "im.send":
            return {"message_id": "om_fake", "chat_id": payload.get("chat_id")}
        if operation == "auth.status":
            return {"status": "ok", "provider": "fake"}
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
    ) -> None:
        self.runner = runner or SubprocessRunner()
        self.timeout_s = timeout_s

    def call(self, operation: str, payload: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
        argv = self._argv(operation, payload, dry_run=dry_run)
        result = self.runner(argv, self.timeout_s)
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
        common = ["--format", "json"]
        if dry_run:
            common.append("--dry-run")
        if operation == "auth.status":
            return ["lark-cli", "auth", "status", *common]
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


class LarkToolAdapter:
    READ_OPS = {"auth.status", "vc.search", "vc.notes", "docs.fetch", "minutes.search", "calendar.agenda"}
    WRITE_OPS = {"docs.create", "task.create", "im.send"}

    def __init__(self, provider: FakeLarkProvider | CliLarkProvider, workspace: Path | str) -> None:
        self.provider = provider
        self.workspace = Path(workspace)
        self.audit_events: list[ToolCallAuditEvent] = []

    @classmethod
    def fake(cls, workspace: Path | str) -> "LarkToolAdapter":
        return cls(FakeLarkProvider(), workspace)

    @classmethod
    def cli(cls, workspace: Path | str) -> "LarkToolAdapter":
        return cls(CliLarkProvider(), workspace)

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
        redacted = re.sub(r"(?i)(app_secret|access_token|refresh_token|authorization|cookie)=\S+", r"\1=[REDACTED]", redacted)
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
