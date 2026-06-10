"""Typed errors for the meeting workflow."""


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


class MissingEvidenceError(AnalyzerValidationError):
    """Raised when confirmed outputs lack transcript evidence."""


class ApprovalRequiredError(MeetingAgentError):
    """Raised when a write operation is attempted without explicit approval."""


class ToolOperationNotAllowedError(MeetingAgentError):
    """Raised when a Lark operation is not in the allowlist."""


class ToolExecutionError(MeetingAgentError):
    """Raised when a Lark provider fails or returns invalid output."""


class PersistenceError(MeetingAgentError):
    """Raised when local meeting memory cannot be read or written."""


class UnauthorizedMeetingWorkflowError(MeetingAgentError):
    """Raised when a user is not allowed to trigger the workflow."""
