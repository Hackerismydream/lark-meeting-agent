"""HTTP wrapper for the macOS Companion API."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from aiohttp import web

from nanobot.meeting.companion_api import CompanionApiService
from nanobot.meeting.repository import SQLiteMeetingRepository

SERVICE_KEY = web.AppKey("companion_service", CompanionApiService)


def create_app(service: CompanionApiService) -> web.Application:
    """Create an aiohttp app that delegates to CompanionApiService."""
    app = web.Application(client_max_size=5 * 1024 * 1024)
    app[SERVICE_KEY] = service
    app.router.add_route("*", "/v1/{tail:.*}", handle_request)
    return app


async def handle_request(request: web.Request) -> web.Response:
    service = request.app[SERVICE_KEY]
    body: dict[str, Any] = {}
    if request.method in {"POST", "PUT", "PATCH"}:
        if request.can_read_body:
            try:
                parsed = await request.json()
            except Exception:
                return web.json_response(
                    {"ok": False, "data": None, "error": {"code": "invalid_json", "message": "Invalid JSON body."}},
                    status=400,
                )
            if not isinstance(parsed, dict):
                return web.json_response(
                    {"ok": False, "data": None, "error": {"code": "invalid_json", "message": "JSON body must be an object."}},
                    status=400,
                )
            body = parsed

    envelope = service.dispatch(
        request.method,
        request.path,
        body=body,
        bearer_token=_bearer_token(request),
    )
    return web.json_response(envelope.model_dump(mode="json"))


def _bearer_token(request: web.Request) -> str | None:
    header = request.headers.get("Authorization", "")
    prefix = "Bearer "
    if header.startswith(prefix):
        return header[len(prefix) :].strip()
    return None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Start the Lark Meeting Agent Companion API server.")
    parser.add_argument("--workspace", default=".", help="Workspace for meeting memory and run state.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--bearer-token", default=None, help="Optional bearer token. Omit for local unauthenticated dev.")
    parser.add_argument("--provider-mode", default="fake")
    parser.add_argument("--analyzer-mode", default="fake")
    parser.add_argument("--sqlite", action="store_true", help="Use SQLite repository instead of JSONL repository.")
    args = parser.parse_args(argv)

    workspace = Path(args.workspace)
    repository = SQLiteMeetingRepository(workspace / ".lark_meeting_agent" / "companion.sqlite") if args.sqlite else None
    service = CompanionApiService(
        workspace,
        bearer_token=args.bearer_token,
        repository=repository,
        provider_mode=args.provider_mode,
        analyzer_mode=args.analyzer_mode,
    )
    web.run_app(create_app(service), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
