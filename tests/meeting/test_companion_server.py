from __future__ import annotations

import pytest

try:
    from aiohttp.test_utils import TestClient, TestServer

    HAS_AIOHTTP = True
except Exception:  # pragma: no cover
    HAS_AIOHTTP = False

from nanobot.meeting.companion_api import CompanionApiService
from nanobot.meeting.companion_server import create_app


pytestmark = pytest.mark.asyncio


TRANSCRIPT = "\n".join(
    [
        "[00:00] Alice: 我们决定先发布本地 demo。",
        "[00:01] Bob: 我负责补充操作手册。",
    ]
)


@pytest.fixture
async def aiohttp_client():
    clients: list[TestClient] = []

    async def make_client(app):
        client = TestClient(TestServer(app))
        await client.start_server()
        clients.append(client)
        return client

    yield make_client

    for client in clients:
        await client.close()


@pytest.mark.skipif(not HAS_AIOHTTP, reason="aiohttp not installed")
async def test_companion_server_status_upload_pending_and_search(tmp_path, aiohttp_client) -> None:
    service = CompanionApiService(tmp_path, bearer_token=None, provider_mode="fake", analyzer_mode="fake")
    client = await aiohttp_client(create_app(service))

    status = await client.get("/v1/agent/status")
    status_payload = await status.json()
    assert status_payload["ok"] is True
    assert status_payload["data"]["companion_api"] == "v1"

    upload = await client.post(
        "/v1/upload/transcript",
        json={"filename": "demo.txt", "content": TRANSCRIPT, "create_doc": True, "create_tasks": True},
    )
    upload_payload = await upload.json()
    assert upload_payload["ok"] is True
    assert upload_payload["data"]["status"] == "approval_required"

    pending = await client.get("/v1/write-plans/pending")
    pending_payload = await pending.json()
    assert pending_payload["ok"] is True
    assert pending_payload["data"]["items"][0]["operations"]

    search = await client.post("/v1/search", json={"question": "有什么待办？"})
    search_payload = await search.json()
    assert search_payload["ok"] is True
    assert "sources" in search_payload["data"]


@pytest.mark.skipif(not HAS_AIOHTTP, reason="aiohttp not installed")
async def test_companion_server_bearer_token(tmp_path, aiohttp_client) -> None:
    service = CompanionApiService(tmp_path, bearer_token="dev-token")
    client = await aiohttp_client(create_app(service))

    denied = await client.get("/v1/agent/status")
    allowed = await client.get("/v1/agent/status", headers={"Authorization": "Bearer dev-token"})

    assert (await denied.json())["error"]["code"] == "unauthorized"
    assert (await allowed.json())["ok"] is True
