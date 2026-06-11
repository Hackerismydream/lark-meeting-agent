from __future__ import annotations

from pathlib import Path

from nanobot.meeting.companion_api import CompanionApiService
from nanobot.meeting.repository import SQLiteMeetingRepository
from nanobot.meeting.schemas import ExecutionStatus, RunStatus


TRANSCRIPT = "\n".join(
    [
        "[00:00] Alice: 我们决定先灰度上线。",
        "[00:01] Bob: 我负责补充风险清单。",
    ]
)


def _service(tmp_path: Path) -> CompanionApiService:
    return CompanionApiService(
        tmp_path,
        bearer_token="dev-token",
        repository=SQLiteMeetingRepository(tmp_path / "meeting.db"),
        actor_id="ou_companion",
        provider_mode="fake",
        analyzer_mode="fake",
    )


def _upload(service: CompanionApiService):
    return service.dispatch(
        "POST",
        "/v1/upload/transcript",
        bearer_token="dev-token",
        body={
            "filename": "demo.txt",
            "content": TRANSCRIPT,
            "create_doc": True,
            "create_tasks": True,
        },
    )


def test_companion_api_requires_bearer_token(tmp_path: Path) -> None:
    service = _service(tmp_path)

    denied = service.dispatch("GET", "/v1/agent/status", bearer_token="wrong-token")
    allowed = service.dispatch("GET", "/v1/agent/status", bearer_token="dev-token")

    assert denied.ok is False
    assert denied.error.code == "unauthorized"
    assert allowed.ok is True
    assert allowed.data["companion_api"] == "v1"


def test_companion_api_upload_lists_run_pending_write_plan_and_trace(tmp_path: Path) -> None:
    service = _service(tmp_path)

    upload = _upload(service)
    run_id = upload.data["run_id"]
    runs = service.dispatch("GET", "/v1/runs", bearer_token="dev-token")
    detail = service.dispatch("GET", f"/v1/runs/{run_id}", bearer_token="dev-token")
    pending = service.dispatch("GET", "/v1/write-plans/pending", bearer_token="dev-token")
    trace = service.dispatch("GET", f"/v1/runs/{run_id}/trace", bearer_token="dev-token")

    assert upload.ok is True
    assert detail.data["status"] == RunStatus.APPROVAL_REQUIRED.value
    assert any(item["run_id"] == run_id for item in runs.data["items"])
    assert pending.data["items"][0]["run_id"] == run_id
    assert pending.data["items"][0]["operations"]
    assert trace.data["events"]


def test_companion_api_approve_selected_operation_ids_goes_through_backend_policy(tmp_path: Path) -> None:
    service = _service(tmp_path)
    upload = _upload(service)
    run_id = upload.data["run_id"]
    pending = service.dispatch("GET", "/v1/write-plans/pending", bearer_token="dev-token")
    operation_id = pending.data["items"][0]["operations"][0]["operation_id"]

    approved = service.dispatch(
        "POST",
        f"/v1/runs/{run_id}/approve",
        bearer_token="dev-token",
        body={"operation_ids": [operation_id]},
    )

    operations = approved.data["write_plan"]["operations"]
    completed = [op for op in operations if op["execution_status"] == ExecutionStatus.COMPLETED.value]
    skipped = [op for op in operations if op["execution_status"] == ExecutionStatus.SKIPPED.value]
    assert approved.ok is True
    assert [op["operation_id"] for op in completed] == [operation_id]
    assert skipped


def test_companion_api_reject_and_search(tmp_path: Path) -> None:
    service = _service(tmp_path)
    upload = _upload(service)
    run_id = upload.data["run_id"]

    rejected = service.dispatch("POST", f"/v1/runs/{run_id}/reject", bearer_token="dev-token", body={})
    answer = service.dispatch("POST", "/v1/search", bearer_token="dev-token", body={"question": "有什么待办？"})

    assert rejected.data["status"] == RunStatus.REJECTED.value
    assert answer.ok is True
    assert answer.data["sources"]


def test_companion_api_upload_rejects_unsupported_file_types(tmp_path: Path) -> None:
    service = _service(tmp_path)

    response = service.dispatch(
        "POST",
        "/v1/upload/transcript",
        bearer_token="dev-token",
        body={"filename": "meeting.mp3", "content": "binary"},
    )

    assert response.ok is False
    assert response.error.code == "unsupported_media_type"
