"""UCX v2 exception hierarchy."""

from __future__ import annotations


class UCXError(Exception):
    """Base exception for all UCX errors."""


class UCXConfigError(UCXError):
    """Configuration is missing or invalid."""


class UCXValidationError(UCXError):
    """Document failed validation and cannot proceed."""

    def __init__(self, message: str, path: str, error_count: int = 0) -> None:
        super().__init__(message)
        self.path = path
        self.error_count = error_count


class UCXDocumentNotFound(UCXError):
    """Requested document path does not exist."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Document not found: {path}")
        self.path = path


class UCXStageError(UCXError):
    """Operation violates the document workflow stage contract."""

    def __init__(self, message: str, required_stage: str, actual_stage: str) -> None:
        super().__init__(message)
        self.required_stage = required_stage
        self.actual_stage = actual_stage


class UCXAIError(UCXError):
    """AI provider call failed."""


class UCXToolError(UCXError):
    """MCP tool execution failed."""
