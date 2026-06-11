from __future__ import annotations

import json
from pathlib import Path

from nanobot.meeting.lark_adapter import LarkToolAdapter
from nanobot.meeting.production import MeetingAgentAccessPolicy, MeetingBotContext, validate_production_config
from nanobot.meeting.security import MeetingSecurityPolicy, redact_secrets, validate_admin_config


def test_admin_config_validation_returns_actionable_findings() -> None:
    findings = validate_admin_config(
        {
            "channels": {"feishu": {"allowFrom": ["*"], "groupPolicy": "open"}},
            "tools": {"exec": {"enable": True}, "restrictToWorkspace": False},
            "meetingAgent": {"writeApprovers": [], "audit": {"enabled": False}},
        }
    )

    by_code = {finding.code: finding for finding in findings}
    assert {
        "wildcard_allow_from",
        "unsafe_group_policy",
        "exec_enabled",
        "workspace_unrestricted",
        "missing_approvers",
        "audit_disabled",
    }.issubset(by_code)
    assert all(finding.action for finding in findings)


def test_legacy_production_config_validation_uses_security_findings() -> None:
    warnings = validate_production_config(
        {
            "channels": {"feishu": {"allowFrom": ["*"]}},
            "tools": {"exec": {"enable": True}, "restrictToWorkspace": False},
            "meetingAgent": {"writeApprovers": [], "audit": {"enabled": False}},
        }
    )

    assert "audit_disabled" in {warning.code for warning in warnings}


def test_meeting_security_policy_separates_permissions() -> None:
    policy = MeetingSecurityPolicy(
        allowed_users={"ou_user"},
        process_users={"ou_process"},
        write_approvers={"ou_write"},
        live_join_approvers={"ou_join"},
        live_leave_approvers={"ou_leave"},
        admin_users={"ou_admin"},
    )

    assert policy.can_use_bot("ou_user")
    assert policy.can_process("ou_process")
    assert not policy.can_approve_writes("ou_process")
    assert policy.can_approve_writes("ou_write")
    assert policy.can_live_join("ou_join")
    assert not policy.can_live_leave("ou_join")
    assert policy.can_live_leave("ou_leave")
    assert policy.can_admin("ou_admin")
    assert policy.can_approve_writes("ou_admin")


def test_meeting_agent_access_policy_exposes_named_permissions() -> None:
    policy = MeetingAgentAccessPolicy(
        allowed_users={"ou_allowed"},
        write_approvers={"ou_write"},
        live_approvers={"ou_live"},
        admin_users={"ou_admin"},
    )

    assert policy.can_use_bot(MeetingBotContext(sender_id="ou_allowed"))
    assert policy.can_process(MeetingBotContext(sender_id="ou_allowed"))
    assert policy.can_approve_writes(MeetingBotContext(sender_id="ou_write"))
    assert policy.can_live_join(MeetingBotContext(sender_id="ou_live"))
    assert policy.can_live_leave(MeetingBotContext(sender_id="ou_live"))
    assert policy.can_admin(MeetingBotContext(sender_id="ou_admin"))


def test_secret_redaction_covers_json_urls_and_bearer_tokens(tmp_path: Path) -> None:
    adapter = LarkToolAdapter.fake(tmp_path)
    raw = json.dumps(
        {
            "access_token": "tenant-token",
            "app_secret": "secret-value",
            "authorization": "Bearer sk-live-secret",
            "url": "https://example.com/callback?token=abc123",
        }
    )

    redacted = redact_secrets(adapter.redact(raw))

    assert "tenant-token" not in redacted
    assert "secret-value" not in redacted
    assert "sk-live-secret" not in redacted
    assert "abc123" not in redacted
    assert "[REDACTED]" in redacted


def test_direct_lark_cli_bypass_absent_outside_adapter() -> None:
    offenders: list[str] = []
    for path in Path("nanobot/meeting").glob("*.py"):
        if path.name in {"lark_adapter.py"}:
            continue
        text = path.read_text()
        if "subprocess" in text or "[\"lark-cli\"" in text or "['lark-cli'" in text:
            offenders.append(str(path))

    assert offenders == []
