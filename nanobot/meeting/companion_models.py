"""Typed models for the macOS companion API."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from nanobot.meeting.schemas import MeetingBaseModel


class ApiError(MeetingBaseModel):
    code: str
    message: str


class ApiEnvelope(MeetingBaseModel):
    ok: bool
    data: dict[str, Any] | list[Any] | None = None
    error: ApiError | None = None

    @classmethod
    def success(cls, data: dict[str, Any] | list[Any] | None = None) -> "ApiEnvelope":
        return cls(ok=True, data=data, error=None)

    @classmethod
    def failure(cls, code: str, message: str) -> "ApiEnvelope":
        return cls(ok=False, data=None, error=ApiError(code=code, message=message))


class ApproveRequest(MeetingBaseModel):
    operation_ids: list[str]


class RejectRequest(MeetingBaseModel):
    reason: str | None = None


class PreBriefRequest(MeetingBaseModel):
    query: str | None = None
    meeting_id: str | None = None
    meeting_type: str = "general"
    project: str | None = None
    customer: str | None = None


class SearchRequest(MeetingBaseModel):
    question: str
    filters: dict[str, Any] = Field(default_factory=dict)


class TranscriptUploadRequest(MeetingBaseModel):
    filename: str
    content: str
    create_doc: bool = True
    create_tasks: bool = True
    send_message: bool = False
    chat_id: str | None = None


class CompanionStatus(MeetingBaseModel):
    status: str = "ok"
    service: str = "lark-meeting-agent"
    companion_api: str = "v1"
    provider_mode: str
    analyzer_mode: str
    storage: str
