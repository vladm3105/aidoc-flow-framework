"""Base Validator protocol for UCX v2.

All layer validators must implement this protocol.
Validators are pure: no side effects, no terminal output, no file writing.
"""

from __future__ import annotations

from typing import Protocol

from ucx.validators.result import ValidationResult


class Validator(Protocol):
    """Structural protocol for UCX document validators.

    Implementations must provide `validate()`. Async variant is optional
    but recommended for validators that perform AI calls.
    """

    def validate(self, content: str, path: str) -> ValidationResult:
        """Validate document content.

        Args:
            content: Full document text.
            path:    Absolute path (used for error context, not for reading).

        Returns:
            ValidationResult with all findings and optional quality score.
        """
        ...
