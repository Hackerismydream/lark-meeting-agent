"""Real live meeting evidence runner."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import Field

from nanobot.meeting.live_lark import LiveLarkMeetingWorkflow, LiveSmokeResult, classify_live_smoke_error
from nanobot.meeting.schemas import ApprovalStatus, MeetingBaseModel, ProviderMode, ToolCallAuditEvent


class LiveEvidenceReport(MeetingBaseModel):
    status: str
    meeting_number: str
    provider_mode: ProviderMode
    approved_visible_join: bool
    approved_visible_leave: bool
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    run_dir: str
    dry_run_join_path: str | None = None
    live_smoke_result_path: str | None = None
    raw_event_shape_path: str | None = None
    audit_path: str | None = None
    blocker_path: str | None = None
    failure_class: str | None = None
    error: str | None = None
    next_actions: list[str] = Field(default_factory=list)


class LiveMeetingEvidenceRunner:
    def __init__(
        self,
        workspace: Path | str,
        *,
        provider_mode: ProviderMode | str = ProviderMode.CLI,
        out_root: Path | str = "runs/live_real",
    ) -> None:
        self.workspace = Path(workspace)
        self.provider_mode = ProviderMode(provider_mode)
        self.out_root = Path(out_root)

    def run(
        self,
        meeting_number: str,
        *,
        approve_visible_join: bool = False,
        approve_visible_leave: bool = False,
    ) -> LiveEvidenceReport:
        normalized = _normalize_meeting_number(meeting_number)
        run_dir = self.out_root / normalized
        run_dir.mkdir(parents=True, exist_ok=True)
        workflow = LiveLarkMeetingWorkflow(self.workspace, self.provider_mode)

        dry_run_path = run_dir / "join_dry_run.json"
        blocker_path: Path | None = None
        raw_event_path = run_dir / "raw_event_shapes.json"
        audit_path = run_dir / "audit.jsonl"
        result_path = run_dir / "live_smoke_result.json"
        try:
            preview = workflow.join(
                meeting_number=normalized,
                dry_run=True,
                approval_status=ApprovalStatus.PENDING,
                title="live evidence dry-run",
            )
            _write_json(
                dry_run_path,
                {
                    "session": preview.model_dump(mode="json"),
                    "provider_preview": _last_audit_result(workflow.adapter.audit_events),
                },
            )
        except Exception as exc:
            _write_json(dry_run_path, {"error": workflow.adapter.redact(str(exc))})

        result = workflow.live_smoke(
            meeting_number=normalized,
            approve_visible_join=approve_visible_join,
            approve_visible_leave=approve_visible_leave,
            export_raw_event_shapes=raw_event_path,
        )
        _write_json(result_path, result.model_dump(mode="json"))
        _write_audit(audit_path, workflow.adapter.audit_events)

        failure_class = result.failure_class
        if result.status in {"blocked", "dry_run", "missing_meeting_number"}:
            blocker_path = run_dir / "blocker.md"
            _write_blocker(blocker_path, normalized, result)
        report = LiveEvidenceReport(
            status=result.status,
            meeting_number=normalized,
            provider_mode=self.provider_mode,
            approved_visible_join=approve_visible_join,
            approved_visible_leave=approve_visible_leave,
            run_dir=str(run_dir),
            dry_run_join_path=str(dry_run_path),
            live_smoke_result_path=str(result_path),
            raw_event_shape_path=str(raw_event_path) if raw_event_path.exists() else None,
            audit_path=str(audit_path),
            blocker_path=str(blocker_path) if blocker_path else None,
            failure_class=failure_class,
            error=result.error,
            next_actions=_next_actions(result),
        )
        _write_json(run_dir / "report.json", report.model_dump(mode="json"))
        return report


def _normalize_meeting_number(meeting_number: str) -> str:
    normalized = "".join(ch for ch in meeting_number if ch.isdigit())
    if len(normalized) != 9:
        raise ValueError("meeting_number must contain exactly 9 digits")
    return normalized


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def _write_audit(path: Path, events: list[ToolCallAuditEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event.model_dump(mode="json"), ensure_ascii=False, default=str) + "\n")


def _last_audit_result(events: list[ToolCallAuditEvent]) -> Any:
    if not events:
        return None
    summary = events[-1].result_summary
    if not summary:
        return None
    try:
        return json.loads(summary)
    except json.JSONDecodeError:
        return summary


def _write_blocker(path: Path, meeting_number: str, result: LiveSmokeResult) -> None:
    failure = result.failure_class or classify_live_smoke_error(result.error or "")
    lines = [
        f"# Live Meeting Blocker: {meeting_number}",
        "",
        f"- status: `{result.status}`",
        f"- failure_class: `{failure}`",
        f"- event_count: `{result.event_count}`",
    ]
    if result.error:
        lines.extend(["", "## Redacted Error", "", "```text", result.error, "```"])
    lines.extend(["", "## Next Actions"])
    lines.extend(f"- {item}" for item in _next_actions(result))
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _next_actions(result: LiveSmokeResult) -> list[str]:
    failure = result.failure_class or classify_live_smoke_error(result.error or "")
    if result.status == "dry_run":
        return ["Rerun with --approve-visible-join and --approve-visible-leave to execute visible join/leave."]
    if failure == "permission":
        return [
            "Confirm the Feishu app has tenant-side access to /vc/v1/bots/join.",
            "Confirm the app is allowed for meeting bot join in the current tenant or gray rollout.",
            "Keep using fixture/live-simulator paths until the tenant permission blocker is cleared.",
        ]
    if failure == "gray":
        return ["Join the Feishu VC agent early-access group or enable the gray feature for this app/tenant."]
    if failure == "meeting_ended":
        return ["Create a new active meeting and rerun the evidence runner while the meeting is still in progress."]
    if failure == "not_in_meeting":
        return ["Ensure join succeeded and use the returned long meeting_id for event polling."]
    if failure == "no_events":
        return ["Speak or send a chat message in the meeting, then rerun event polling."]
    return ["Inspect report.json and audit.jsonl, then add a narrower classifier if the failure repeats."]
