"""UCX custom exceptions."""

from typing import Optional, Any


class UCXError(Exception):
    """Base exception for all UCX errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class ConfigurationError(UCXError):
    """Raised when configuration is invalid."""

    pass


class ValidationError(UCXError):
    """Raised when document validation fails."""

    def __init__(
        self,
        message: str,
        errors: Optional[list[str]] = None,
        warnings: Optional[list[str]] = None,
    ):
        super().__init__(message)
        self.errors = errors or []
        self.warnings = warnings or []


class AIClientError(UCXError):
    """Raised when AI client operation fails."""

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        super().__init__(message)
        self.model = model
        self.status_code = status_code


class PromptError(UCXError):
    """Raised when prompt loading or rendering fails."""

    def __init__(self, message: str, prompt_name: Optional[str] = None):
        super().__init__(message)
        self.prompt_name = prompt_name


class SkillError(UCXError):
    """Raised when skill loading fails."""

    def __init__(self, message: str, skill_name: Optional[str] = None):
        super().__init__(message)
        self.skill_name = skill_name


class DriftDetectedError(UCXError):
    """Raised when upstream drift is detected."""

    def __init__(
        self,
        message: str,
        changed_files: Optional[list[str]] = None,
    ):
        super().__init__(message)
        self.changed_files = changed_files or []


class PhaseError(UCXError):
    """Raised when a UCX phase fails."""

    def __init__(
        self,
        message: str,
        phase: str,
        iteration: Optional[int] = None,
    ):
        super().__init__(message)
        self.phase = phase
        self.iteration = iteration
