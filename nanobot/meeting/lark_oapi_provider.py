"""OpenAPI-backed Lark provider behind LarkToolAdapter."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from nanobot.meeting.errors import ToolExecutionError
from nanobot.meeting.schemas import ProviderMode

WRITE_OP_NAMES = {"docs.create", "task.create", "im.send", "vc.meeting.join", "vc.meeting.leave"}


@dataclass
class OapiRequest:
    method: str
    path: str
    params: dict[str, Any]
    body: dict[str, Any]


class OapiProviderError(ToolExecutionError):
    """Classified Lark OpenAPI provider failure."""

    def __init__(self, kind: str, message: str, *, status_code: int | None = None) -> None:
        self.kind = kind
        self.status_code = status_code
        super().__init__(f"{kind}: {message}")


def classify_oapi_error(message: str, status_code: int | None = None) -> str:
    normalized = message.lower()
    if status_code in {401, 10014} or "invalid token" in normalized or "unauthorized" in normalized:
        return "invalid_token"
    if "scope" in normalized or "permission scope" in normalized:
        return "missing_scope"
    if status_code == 403 or "permission" in normalized or "forbidden" in normalized:
        return "permission_denied"
    if status_code == 429 or "rate limit" in normalized or "too many requests" in normalized:
        return "rate_limit"
    if status_code and status_code >= 500:
        return "unavailable"
    if "timeout" in normalized or "temporarily unavailable" in normalized or "connection" in normalized:
        return "unavailable"
    return "unavailable"


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
            kind = classify_oapi_error(body, status_code=exc.code)
            raise OapiProviderError(kind, f"HTTP {exc.code}: {body}", status_code=exc.code) from exc
        except urllib.error.URLError as exc:
            message = str(exc.reason)
            raise OapiProviderError(classify_oapi_error(message), f"request failed: {message}") from exc
        parsed = _parse_json_object(payload, "Lark OpenAPI")
        code = parsed.get("code")
        if code not in {None, 0}:
            message = str(parsed.get("msg") or parsed.get("message") or parsed)
            raise OapiProviderError(classify_oapi_error(message, status_code=code if isinstance(code, int) else None), message)
        return parsed


class OapiLarkProvider:
    mode = ProviderMode.OAPI

    def __init__(
        self,
        *,
        access_token: str | None = None,
        base_url: str = "https://open.feishu.cn",
        runner: Any | None = None,
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
            raise OapiProviderError("invalid_token", "LARK_OAPI_ACCESS_TOKEN is required for OAPI provider")
        return self.runner(base_url=self.base_url, request=request, token=self.access_token, timeout_s=self.timeout_s)

    def _request(self, operation: str, payload: dict[str, Any]) -> OapiRequest:
        if operation == "calendar.agenda":
            return OapiRequest(
                method="GET",
                path="/open-apis/calendar/v4/calendars/primary/events",
                params={"start_time": payload.get("start"), "end_time": payload.get("end"), "summary": payload.get("query")},
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
            meeting_id = _require_any(payload, "meeting_id", "minute_token")
            return OapiRequest(
                method="GET",
                path=f"/open-apis/vc/v1/meetings/{urllib.parse.quote(str(meeting_id), safe='')}/notes",
                params={},
                body={},
            )
        if operation == "vc.meeting.join":
            body = {"meeting_number": _require(payload, "meeting_number")}
            if password := payload.get("password"):
                body["password"] = password
            return OapiRequest(method="POST", path="/open-apis/vc/v1/bots/join", params={}, body=body)
        if operation == "vc.meeting.events":
            return OapiRequest(
                method="GET",
                path="/open-apis/vc/v1/bots/events",
                params={
                    "meeting_id": _require(payload, "meeting_id"),
                    "start_time": payload.get("start"),
                    "end_time": payload.get("end"),
                    "page_token": payload.get("page_token"),
                    "page_size": payload.get("page_size"),
                },
                body={},
            )
        if operation == "vc.meeting.leave":
            return OapiRequest(method="POST", path="/open-apis/vc/v1/bots/leave", params={}, body={"meeting_id": _require(payload, "meeting_id")})
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
            return OapiRequest(method="GET", path="/open-apis/search/v2/data_search", params={"query": payload.get("query"), "data_types": "doc,docx"}, body={})
        if operation == "docs.fetch":
            doc = _require_any(payload, "doc", "token")
            return OapiRequest(
                method="GET",
                path=f"/open-apis/docx/v1/documents/{urllib.parse.quote(str(doc), safe='')}/raw_content",
                params={},
                body={},
            )
        if operation in {"task.search", "task.list"}:
            return OapiRequest(method="GET", path="/open-apis/task/v2/tasks", params={"summary": payload.get("query"), "status": payload.get("status")}, body={})
        if operation == "docs.create":
            return OapiRequest(
                method="POST",
                path="/open-apis/docx/v1/documents",
                params={},
                body={"title": _require(payload, "title"), "content": _require(payload, "markdown")},
            )
        if operation == "task.create":
            body = {"summary": _require(payload, "summary"), "description": payload.get("description") or ""}
            if due := payload.get("due"):
                body["due"] = due
            if assignee := payload.get("assignee"):
                body["assignee"] = assignee
            return OapiRequest(method="POST", path="/open-apis/task/v2/tasks", params={}, body=body)
        if operation == "im.send":
            chat_id = _require(payload, "chat_id")
            content = {"text": _require_any(payload, "markdown", "text")}
            return OapiRequest(
                method="POST",
                path="/open-apis/im/v1/messages",
                params={"receive_id_type": "chat_id"},
                body={"receive_id": chat_id, "msg_type": "text", "content": json.dumps(content, ensure_ascii=False)},
            )
        from nanobot.meeting.errors import ToolOperationNotAllowedError

        raise ToolOperationNotAllowedError(f"operation not allowlisted: {operation}")


def _parse_json_object(payload: str, source: str) -> dict[str, Any]:
    try:
        parsed = json.loads(payload or "{}")
    except json.JSONDecodeError as exc:
        raise OapiProviderError("unavailable", f"{source} returned malformed JSON") from exc
    if not isinstance(parsed, dict):
        raise OapiProviderError("unavailable", f"{source} JSON output must be an object")
    return parsed


def _require(payload: dict[str, Any], key: str) -> Any:
    value = payload.get(key)
    if value is None or value == "":
        raise ToolExecutionError(f"{key} is required")
    return value


def _require_any(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = payload.get(key)
        if value is not None and value != "":
            return value
    raise ToolExecutionError(f"one of {', '.join(keys)} is required")
