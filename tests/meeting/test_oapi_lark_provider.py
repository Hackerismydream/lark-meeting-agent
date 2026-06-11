from __future__ import annotations

import pytest

from nanobot.meeting.errors import ToolExecutionError
from nanobot.meeting.lark_adapter import LarkToolAdapter, OapiRequest
from nanobot.meeting.lark_oapi_provider import OapiLarkProvider, OapiProviderError, classify_oapi_error
from nanobot.meeting.schemas import ApprovalStatus


def test_oapi_provider_schema_validates_required_write_fields() -> None:
    provider = OapiLarkProvider(access_token="tenant-token")

    with pytest.raises(ToolExecutionError, match="markdown is required"):
        provider.call("docs.create", {"title": "会议纪要"}, dry_run=True)

    with pytest.raises(ToolExecutionError, match="summary is required"):
        provider.call("task.create", {"description": "补充风险"}, dry_run=True)

    with pytest.raises(ToolExecutionError, match="chat_id is required"):
        provider.call("im.send", {"text": "会议纪要已生成"}, dry_run=True)


def test_oapi_provider_schema_validates_live_required_fields() -> None:
    provider = OapiLarkProvider(access_token="tenant-token")

    with pytest.raises(ToolExecutionError, match="meeting_number is required"):
        provider.call("vc.meeting.join", {}, dry_run=True)

    with pytest.raises(ToolExecutionError, match="meeting_id is required"):
        provider.call("vc.meeting.events", {}, dry_run=False)

    with pytest.raises(ToolExecutionError, match="meeting_id is required"):
        provider.call("vc.meeting.leave", {}, dry_run=True)


def test_oapi_provider_classifies_openapi_errors() -> None:
    assert classify_oapi_error("invalid token", status_code=401) == "invalid_token"
    assert classify_oapi_error("missing required scope vc:meeting.read", status_code=403) == "missing_scope"
    assert classify_oapi_error("permission denied", status_code=403) == "permission_denied"
    assert classify_oapi_error("rate limit exceeded", status_code=429) == "rate_limit"
    assert classify_oapi_error("server error", status_code=503) == "unavailable"


def test_oapi_runner_error_kind_is_preserved_in_adapter_audit(tmp_path) -> None:
    def runner(*, base_url: str, request: OapiRequest, token: str, timeout_s: int) -> dict:
        raise OapiProviderError("missing_scope", "missing required scope vc:meeting.read")

    adapter = LarkToolAdapter.oapi(workspace=tmp_path, access_token="tenant-token", runner=runner)

    with pytest.raises(OapiProviderError) as exc_info:
        adapter.execute("vc.search", {"query": "项目例会"})

    assert exc_info.value.kind == "missing_scope"
    assert adapter.audit_events[-1].execution_status == "failed"
    assert "missing_scope" in (adapter.audit_events[-1].error_message or "")


def test_oapi_adapter_redacts_tokens_from_audit_result_summary(tmp_path) -> None:
    def runner(*, base_url: str, request: OapiRequest, token: str, timeout_s: int) -> dict:
        return {"access_token": "secret-token", "authorization": "Bearer sk-secret", "items": []}

    adapter = LarkToolAdapter.oapi(workspace=tmp_path, access_token="tenant-token", runner=runner)

    adapter.execute("vc.search", {"query": "项目例会"})
    audit_json = adapter.audit_events[-1].model_dump_json()

    assert "secret-token" not in audit_json
    assert "sk-secret" not in audit_json
    assert "[REDACTED]" in audit_json


def test_oapi_approved_write_calls_runner_with_valid_request(tmp_path) -> None:
    seen: dict[str, object] = {}

    def runner(*, base_url: str, request: OapiRequest, token: str, timeout_s: int) -> dict:
        seen["request"] = request
        seen["token"] = token
        return {"message_id": "om_1"}

    adapter = LarkToolAdapter.oapi(workspace=tmp_path, access_token="tenant-token", runner=runner)
    result = adapter.execute(
        "im.send",
        {"chat_id": "oc_safe", "text": "会议纪要已生成"},
        dry_run=False,
        approval_status=ApprovalStatus.APPROVED,
    )

    request = seen["request"]
    assert result == {"message_id": "om_1"}
    assert isinstance(request, OapiRequest)
    assert request.method == "POST"
    assert request.path == "/open-apis/im/v1/messages"
    assert seen["token"] == "tenant-token"
