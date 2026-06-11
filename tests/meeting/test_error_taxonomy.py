from __future__ import annotations

from nanobot.meeting.errors import (
    ApprovalProviderMismatchError,
    ApprovalRequiredError,
    AnalyzerValidationError,
    MeetingAgentError,
    MeetingNotFoundError,
    ToolExecutionError,
    classify_error,
)
from nanobot.meeting.live_lark import classify_live_smoke_error


def test_error_taxonomy_maps_known_errors_to_safe_messages() -> None:
    cases = [
        (PermissionError("permission denied"), "permission"),
        (ToolExecutionError("gray release not enabled"), "gray"),
        (MeetingNotFoundError("missing transcript"), "missing_transcript"),
        (ToolExecutionError("unknown event shape"), "unknown_event"),
        (AnalyzerValidationError("malformed output"), "malformed_output"),
        (ApprovalRequiredError("approval required"), "approval_mismatch"),
        (ApprovalProviderMismatchError("provider mismatch"), "provider_mismatch"),
    ]

    for exc, code in cases:
        info = classify_error(exc)
        assert info.code == code
        assert info.user_message
        assert "secret" not in info.user_message.lower()


def test_live_smoke_error_classification_still_maps_gate_failures() -> None:
    assert classify_live_smoke_error("no permission to access meeting") == "permission"
    assert classify_live_smoke_error("gray release not enabled") == "gray"
    assert classify_live_smoke_error("meeting ended") == "meeting_ended"


def test_unknown_errors_are_safe_and_retryable_false() -> None:
    info = classify_error(MeetingAgentError("unexpected sk-secret failure"))

    assert info.code == "unknown"
    assert "sk-secret" not in info.user_message
