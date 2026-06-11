"""Security and governance helpers for production meeting workflows."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class SecurityFinding:
    code: str
    severity: Literal["warning", "error"]
    message: str
    action: str


@dataclass
class MeetingSecurityPolicy:
    allowed_users: set[str] = field(default_factory=set)
    process_users: set[str] = field(default_factory=set)
    write_approvers: set[str] = field(default_factory=set)
    live_join_approvers: set[str] = field(default_factory=set)
    live_leave_approvers: set[str] = field(default_factory=set)
    admin_users: set[str] = field(default_factory=set)

    def can_use_bot(self, sender_id: str) -> bool:
        return sender_id in self.admin_users or sender_id in self.allowed_users or self.can_process(sender_id)

    def can_process(self, sender_id: str) -> bool:
        return sender_id in self.admin_users or sender_id in self.process_users or sender_id in self.allowed_users

    def can_approve_writes(self, sender_id: str) -> bool:
        return sender_id in self.admin_users or sender_id in self.write_approvers

    def can_live_join(self, sender_id: str) -> bool:
        return sender_id in self.admin_users or sender_id in self.live_join_approvers

    def can_live_leave(self, sender_id: str) -> bool:
        return sender_id in self.admin_users or sender_id in self.live_leave_approvers

    def can_admin(self, sender_id: str) -> bool:
        return sender_id in self.admin_users


def validate_admin_config(config: dict) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    channels = config.get("channels", {})
    feishu = channels.get("feishu", {}) if isinstance(channels, dict) else {}
    allow_from = feishu.get("allowFrom", [])
    if "*" in allow_from:
        findings.append(
            SecurityFinding(
                code="wildcard_allow_from",
                severity="error",
                message="Feishu allowFrom contains wildcard.",
                action="Replace '*' with explicit user IDs or pairing-only access.",
            )
        )
    if feishu.get("groupPolicy") == "open":
        findings.append(
            SecurityFinding(
                code="unsafe_group_policy",
                severity="warning",
                message="Feishu group policy is open.",
                action="Use mention/topic-scoped group policy for production groups.",
            )
        )
    tools = config.get("tools", {})
    exec_cfg = tools.get("exec", {}) if isinstance(tools, dict) else {}
    if exec_cfg.get("enable") is not False:
        findings.append(
            SecurityFinding(
                code="exec_enabled",
                severity="error",
                message="Production config should disable generic exec tools.",
                action="Set tools.exec.enable=false.",
            )
        )
    if tools.get("restrictToWorkspace") is not True:
        findings.append(
            SecurityFinding(
                code="workspace_unrestricted",
                severity="error",
                message="Production config should restrict tools to the workspace.",
                action="Set tools.restrictToWorkspace=true.",
            )
        )
    meeting = config.get("meetingAgent", {})
    if not meeting.get("writeApprovers"):
        findings.append(
            SecurityFinding(
                code="missing_approvers",
                severity="error",
                message="No write approvers configured.",
                action="Configure meetingAgent.writeApprovers with explicit user IDs.",
            )
        )
    audit_cfg = meeting.get("audit", {}) if isinstance(meeting, dict) else {}
    if audit_cfg.get("enabled") is not True:
        findings.append(
            SecurityFinding(
                code="audit_disabled",
                severity="error",
                message="Audit logging is not explicitly enabled.",
                action="Set meetingAgent.audit.enabled=true and verify persistence.",
            )
        )
    return findings


def redact_secrets(value: str) -> str:
    redacted = re.sub(r"sk-[A-Za-z0-9_\-]+", "[REDACTED]", value)
    redacted = re.sub(
        r'(?i)"(app_secret|access_token|refresh_token|authorization|cookie|token|secret)"\s*:\s*"[^"]*"',
        r'"\1": "[REDACTED]"',
        redacted,
    )
    redacted = re.sub(
        r"(?i)(app_secret|access_token|refresh_token|authorization|cookie|token|secret)=([^&\s]+)",
        r"\1=[REDACTED]",
        redacted,
    )
    redacted = re.sub(r"(?i)Bearer\s+[A-Za-z0-9_.\-]+", "Bearer [REDACTED]", redacted)
    redacted = re.sub(r"https://[^\s\"']*(?:token|secret|auth)[^\s\"']*", "https://[REDACTED]", redacted)
    return redacted
