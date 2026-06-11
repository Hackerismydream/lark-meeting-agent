"""Typed errors for the meeting workflow."""

from __future__ import annotations

from dataclasses import dataclass

from nanobot.meeting.security import redact_secrets


class MeetingAgentError(Exception):
    """Base error for Lark Meeting Agent failures."""


class MeetingNotFoundError(MeetingAgentError):
    """Raised when a requested meeting cannot be resolved."""


class TranscriptNotFoundError(MeetingAgentError):
    """Raised when a meeting has no transcript or minutes content."""


class TranscriptNormalizationError(MeetingAgentError):
    """Raised when transcript input cannot be normalized."""


class AnalyzerValidationError(MeetingAgentError):
    """Raised when analyzer output fails schema or evidence validation."""


class EvidenceValidationError(AnalyzerValidationError):
    """Raised when analyzer evidence cannot be grounded in transcript segments."""


class MissingEvidenceError(AnalyzerValidationError):
    """Raised when confirmed outputs lack transcript evidence."""


class ApprovalRequiredError(MeetingAgentError):
    """Raised when a write operation is attempted without explicit approval."""


class ApprovalProviderMismatchError(MeetingAgentError):
    """Raised when approval tries to use a provider different from the run snapshot."""


class ToolOperationNotAllowedError(MeetingAgentError):
    """Raised when a Lark operation is not in the allowlist."""


class ToolExecutionError(MeetingAgentError):
    """Raised when a Lark provider fails or returns invalid output."""


class PersistenceError(MeetingAgentError):
    """Raised when local meeting memory cannot be read or written."""


class UnauthorizedMeetingWorkflowError(MeetingAgentError):
    """Raised when a user is not allowed to trigger the workflow."""


@dataclass(frozen=True)
class ErrorInfo:
    code: str
    user_message: str
    retryable: bool = False


def classify_error(error: Exception) -> ErrorInfo:
    message = redact_secrets(str(error))
    lowered = message.lower()
    if isinstance(error, PermissionError) or "permission" in lowered or "forbidden" in lowered:
        return ErrorInfo("permission", "没有权限访问或执行该会议操作。", retryable=False)
    if "gray" in lowered or "灰度" in message:
        return ErrorInfo("gray", "该租户或账号尚未开放所需能力。", retryable=False)
    if isinstance(error, (MeetingNotFoundError, TranscriptNotFoundError)) or "missing transcript" in lowered:
        return ErrorInfo("missing_transcript", "没有找到可用的会议转写或会议内容。", retryable=False)
    if "unknown event" in lowered or "event shape" in lowered:
        return ErrorInfo("unknown_event", "收到未知的会议事件格式，需要记录样本后适配。", retryable=False)
    if isinstance(error, AnalyzerValidationError) or "malformed" in lowered or "invalid json" in lowered:
        return ErrorInfo("malformed_output", "模型或外部系统返回格式不合法，已拒绝使用该输出。", retryable=True)
    if isinstance(error, ApprovalRequiredError):
        return ErrorInfo("approval_mismatch", "写操作缺少明确审批，未执行。", retryable=False)
    if isinstance(error, ApprovalProviderMismatchError):
        return ErrorInfo("provider_mismatch", "审批使用的 provider 与 run 记录不一致，未执行。", retryable=False)
    return ErrorInfo("unknown", f"操作失败：{message}", retryable=False)
