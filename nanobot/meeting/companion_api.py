"""Thin backend adapter for macOS companion clients."""

from __future__ import annotations

import re
from contextlib import nullcontext
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from nanobot.meeting.companion_models import (
    ApiEnvelope,
    ApproveRequest,
    CompanionStatus,
    PreBriefRequest,
    RejectRequest,
    SearchRequest,
    TranscriptUploadRequest,
)
from nanobot.meeting.errors import classify_error
from nanobot.meeting.memory import MeetingMemoryStore
from nanobot.meeting.prebrief import PreBriefWorkflow
from nanobot.meeting.production import MeetingAgentAccessPolicy, MeetingBotContext, ProductionMeetingBot
from nanobot.meeting.repository import JsonlMeetingRepository, MeetingRepository
from nanobot.meeting.schemas import MeetingRef, MeetingRefType, MeetingType, PreBriefInput, ProcessMeetingInput, RunStatus
from nanobot.meeting.tracing import TraceReader
from nanobot.meeting.workflow import PostMeetingWorkflow


class CompanionApiService:
    """In-process Companion API adapter.

    A future HTTP server can delegate to this class. The class itself does not
    run an Agent loop and does not call Lark APIs directly.
    """

    def __init__(
        self,
        workspace: Path | str,
        *,
        bearer_token: str | None,
        repository: MeetingRepository | None = None,
        policy: MeetingAgentAccessPolicy | None = None,
        actor_id: str = "companion-user",
        provider_mode: str = "fake",
        analyzer_mode: str = "fake",
    ) -> None:
        self.workspace = Path(workspace)
        self.bearer_token = bearer_token
        self.repository = repository or JsonlMeetingRepository(self.workspace)
        self.policy = policy or MeetingAgentAccessPolicy(allowed_users={actor_id}, write_approvers={actor_id}, admin_users={actor_id})
        self.actor_id = actor_id
        self.provider_mode = provider_mode
        self.analyzer_mode = analyzer_mode

    def dispatch(self, method: str, path: str, *, body: dict[str, Any] | None = None, bearer_token: str | None = None) -> ApiEnvelope:
        if not self._authorized(bearer_token):
            return ApiEnvelope.failure("unauthorized", "Missing or invalid bearer token.")
        try:
            return self._dispatch_authorized(method.upper(), path, body or {})
        except ValidationError as exc:
            return ApiEnvelope.failure("validation_error", str(exc))
        except Exception as exc:
            info = classify_error(exc)
            return ApiEnvelope.failure(info.code, info.user_message)

    def _dispatch_authorized(self, method: str, path: str, body: dict[str, Any]) -> ApiEnvelope:
        if method == "GET" and path == "/v1/agent/status":
            return self.status()
        if method == "GET" and path == "/v1/meetings/today":
            return self.meetings_today()
        if method == "POST" and path == "/v1/prebrief":
            return self.prebrief(PreBriefRequest.model_validate(body))
        if method == "GET" and path == "/v1/runs":
            return self.list_runs()
        if method == "GET" and path == "/v1/write-plans/pending":
            return self.pending_write_plans()
        if method == "POST" and path == "/v1/search":
            return self.search(SearchRequest.model_validate(body))
        if method == "POST" and path == "/v1/upload/transcript":
            return self.upload_transcript(TranscriptUploadRequest.model_validate(body))
        if match := re.fullmatch(r"/v1/runs/([^/]+)", path):
            run_id = match.group(1)
            if method == "GET":
                return self.get_run(run_id)
        if match := re.fullmatch(r"/v1/runs/([^/]+)/trace", path):
            if method == "GET":
                return self.get_trace(match.group(1))
        if match := re.fullmatch(r"/v1/runs/([^/]+)/approve", path):
            if method == "POST":
                return self.approve(match.group(1), ApproveRequest.model_validate(body))
        if match := re.fullmatch(r"/v1/runs/([^/]+)/reject", path):
            if method == "POST":
                return self.reject(match.group(1), RejectRequest.model_validate(body))
        return ApiEnvelope.failure("not_found", f"No companion API route for {method} {path}.")

    def status(self) -> ApiEnvelope:
        payload = CompanionStatus(
            provider_mode=self.provider_mode,
            analyzer_mode=self.analyzer_mode,
            storage=self.repository.__class__.__name__,
        )
        return ApiEnvelope.success(payload.model_dump(mode="json"))

    def meetings_today(self) -> ApiEnvelope:
        return ApiEnvelope.success({"items": [], "source": "not_configured"})

    def prebrief(self, request: PreBriefRequest) -> ApiEnvelope:
        ref = MeetingRef(
            type=MeetingRefType.MEETING_ID if request.meeting_id else MeetingRefType.LATEST_ENDED,
            value=request.meeting_id,
            query=request.query,
        )
        result = PreBriefWorkflow(self.workspace, self.provider_mode).generate(
            PreBriefInput(
                meeting_ref=ref,
                provider_mode=self.provider_mode,
                meeting_type=MeetingType(request.meeting_type),
                project=request.project,
                customer=request.customer,
            )
        )
        return ApiEnvelope.success(result.model_dump(mode="json"))

    def list_runs(self) -> ApiEnvelope:
        runs = [run.model_dump(mode="json") for run in self.repository.list_runs(limit=20)]
        return ApiEnvelope.success({"items": runs})

    def get_run(self, run_id: str) -> ApiEnvelope:
        return ApiEnvelope.success(self.repository.load_run(run_id).model_dump(mode="json"))

    def get_trace(self, run_id: str) -> ApiEnvelope:
        return ApiEnvelope.success(TraceReader(self.workspace).load(run_id).model_dump(mode="json"))

    def pending_write_plans(self) -> ApiEnvelope:
        runs = self.repository.list_runs(status=RunStatus.APPROVAL_REQUIRED.value, limit=20)
        items = []
        for run in runs:
            operations = run.write_plan.operations if run.write_plan else []
            items.append({"run_id": run.run_id, "status": run.status.value, "operations": [op.model_dump(mode="json") for op in operations]})
        return ApiEnvelope.success({"items": items})

    def approve(self, run_id: str, request: ApproveRequest) -> ApiEnvelope:
        if not request.operation_ids:
            return ApiEnvelope.failure("validation_error", "operation_ids must not be empty.")
        reply = ProductionMeetingBot(
            self.workspace,
            self.policy,
            repository=self.repository,
            provider_mode=self.provider_mode,
            analyzer_mode=self.analyzer_mode,
        ).handle_message(self._context(), f"/meeting approve {run_id} " + " ".join(request.operation_ids))
        if reply.status == "denied":
            return ApiEnvelope.failure("permission", reply.text)
        return self.get_run(run_id)

    def reject(self, run_id: str, request: RejectRequest) -> ApiEnvelope:
        del request
        reply = ProductionMeetingBot(
            self.workspace,
            self.policy,
            repository=self.repository,
            provider_mode=self.provider_mode,
            analyzer_mode=self.analyzer_mode,
        ).handle_message(self._context(), f"/meeting reject {run_id}")
        if reply.status == "denied":
            return ApiEnvelope.failure("permission", reply.text)
        return self.get_run(run_id)

    def search(self, request: SearchRequest) -> ApiEnvelope:
        answer = MeetingMemoryStore(self.workspace).qa(request.question)
        return ApiEnvelope.success(answer.model_dump(mode="json"))

    def upload_transcript(self, request: TranscriptUploadRequest) -> ApiEnvelope:
        suffix = Path(request.filename).suffix.lower()
        if suffix not in {".txt", ".md", ".json"}:
            return ApiEnvelope.failure("unsupported_media_type", "Only .txt, .md, and .json transcript uploads are supported.")
        upload_dir = self.workspace / ".lark_meeting_agent" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(request.filename).name)
        upload_path = upload_dir / safe_name
        upload_path.write_text(request.content)
        result = PostMeetingWorkflow(self.workspace, self.provider_mode, self.analyzer_mode).process(
            ProcessMeetingInput(
                meeting_ref=MeetingRef(type=MeetingRefType.TRANSCRIPT_FILE, value=str(upload_path)),
                provider_mode=self.provider_mode,
                analyzer_mode=self.analyzer_mode,
                create_doc=request.create_doc,
                create_tasks=request.create_tasks,
                send_message=request.send_message,
                chat_id=request.chat_id,
                dry_run=True,
            )
        )
        run = MeetingMemoryStore(self.workspace).load_run_snapshot(result.run_id)
        self.repository.save_run(run)
        return ApiEnvelope.success(result.model_dump(mode="json"))

    def _authorized(self, bearer_token: str | None) -> bool:
        if self.bearer_token is None:
            return True
        return bearer_token == self.bearer_token

    def _context(self) -> MeetingBotContext:
        return MeetingBotContext(sender_id=self.actor_id, chat_type="dm")
