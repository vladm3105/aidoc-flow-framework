"""Validation result data models for UCX v2.

All validators return ValidationResult. MCP tools serialize these to dicts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    """Finding severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Finding:
    """A single validation finding.

    Attributes:
        code:     Gate code (e.g. "GATE-01", "BRD-ID-001")
        message:  Human-readable description
        severity: Error, warning, or informational
        line:     Source line number if applicable
        context:  Surrounding text snippet if applicable
    """

    code: str
    message: str
    severity: Severity
    line: int | None = None
    context: str | None = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "line": self.line,
            "context": self.context,
        }


@dataclass
class ValidationResult:
    """Result of a document validation run.

    Attributes:
        valid:    True if no ERROR-severity findings were produced
        path:     Absolute path of the validated document
        findings: All findings (errors, warnings, info)
        score:    Quality score 0.0–1.0 if scoring was performed
    """

    valid: bool
    path: str
    findings: list[Finding] = field(default_factory=list)
    score: float | None = None

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.WARNING]

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "path": self.path,
            "findings": [f.to_dict() for f in self.findings],
            "score": self.score,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
        }
