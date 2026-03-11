"""Validation result classes for UCX unified validators.

Provides:
- ValidationIssue: Individual validation issue with code, severity, location
- UnifiedValidationResult: Tiered validation results (Tier 1/Tier 2)
- ValidationTier: Tier classification enum
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ucx.validators.common.error_codes import Severity, get_error


class ValidationTier(Enum):
    """Validation tier classification."""

    TIER1 = "tier1"  # Core checks (blocking)
    TIER2 = "tier2"  # Advisory checks (non-blocking)


@dataclass
class ValidationIssue:
    """Individual validation issue."""

    code: str
    message: str
    severity: Severity
    file_path: Optional[Path] = None
    line: Optional[int] = None
    context: str = ""
    tier: ValidationTier = ValidationTier.TIER1

    @classmethod
    def from_code(
        cls,
        code: str,
        file_path: Optional[Path] = None,
        line: Optional[int] = None,
        context: str = "",
        tier: ValidationTier = ValidationTier.TIER1,
    ) -> "ValidationIssue":
        """
        Create issue from error code.

        Args:
            code: Error code (e.g., 'BRD-E001')
            file_path: Source file path
            line: Line number
            context: Additional context
            tier: Validation tier

        Returns:
            ValidationIssue instance
        """
        error = get_error(code)
        if error:
            return cls(
                code=code,
                message=error.message,
                severity=error.severity,
                file_path=file_path,
                line=line,
                context=context,
                tier=tier,
            )
        # Unknown code - treat as error
        return cls(
            code=code,
            message=f"Unknown error code: {code}",
            severity=Severity.ERROR,
            file_path=file_path,
            line=line,
            context=context,
            tier=tier,
        )

    def format(self, include_remediation: bool = True) -> str:
        """Format issue for display."""
        severity_label = {
            Severity.ERROR: "ERROR",
            Severity.WARNING: "WARNING",
            Severity.INFO: "INFO",
        }[self.severity]

        # Build location string
        location = ""
        if self.file_path:
            location = str(self.file_path)
            if self.line:
                location += f":{self.line}"
            location += " "

        # Build message
        msg = f"[{severity_label}] {self.code}: {location}{self.message}"

        if self.context:
            msg += f" ({self.context})"

        if include_remediation:
            error = get_error(self.code)
            if error:
                msg += f" - {error.remediation}"

        return msg

    @property
    def is_error(self) -> bool:
        """Check if this is an error (not warning/info)."""
        return self.severity == Severity.ERROR

    @property
    def is_warning(self) -> bool:
        """Check if this is a warning."""
        return self.severity == Severity.WARNING


@dataclass
class UnifiedValidationResult:
    """Tiered validation result for unified validators."""

    doc_path: Path
    tier1_issues: List[ValidationIssue] = field(default_factory=list)
    tier2_issues: List[ValidationIssue] = field(default_factory=list)
    passes: List[str] = field(default_factory=list)
    checks_run: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def tier1_errors(self) -> List[ValidationIssue]:
        """Get Tier 1 errors."""
        return [i for i in self.tier1_issues if i.is_error]

    @property
    def tier1_warnings(self) -> List[ValidationIssue]:
        """Get Tier 1 warnings."""
        return [i for i in self.tier1_issues if i.is_warning]

    @property
    def tier2_errors(self) -> List[ValidationIssue]:
        """Get Tier 2 errors (promoted warnings in strict mode)."""
        return [i for i in self.tier2_issues if i.is_error]

    @property
    def tier2_warnings(self) -> List[ValidationIssue]:
        """Get Tier 2 warnings."""
        return [i for i in self.tier2_issues if i.is_warning]

    @property
    def all_errors(self) -> List[ValidationIssue]:
        """Get all errors (both tiers)."""
        return self.tier1_errors + self.tier2_errors

    @property
    def all_warnings(self) -> List[ValidationIssue]:
        """Get all warnings (both tiers)."""
        return self.tier1_warnings + self.tier2_warnings

    @property
    def has_tier1_errors(self) -> bool:
        """Check if Tier 1 errors exist."""
        return len(self.tier1_errors) > 0

    @property
    def has_errors(self) -> bool:
        """Check if any errors exist."""
        return len(self.all_errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if any warnings exist."""
        return len(self.all_warnings) > 0

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no Tier 1 errors)."""
        return not self.has_tier1_errors

    def exit_code(self, strict: bool = False) -> int:
        """
        Calculate exit code.

        Args:
            strict: If True, treat warnings as errors

        Returns:
            0 = pass, 1 = warnings, 2 = errors, 3 = script error
        """
        if self.tier1_errors:
            return 2
        if strict and (self.tier1_warnings or self.tier2_warnings):
            return 2
        if self.tier1_warnings or self.tier2_warnings:
            return 1
        return 0

    @property
    def status(self) -> str:
        """Get status string."""
        if self.has_tier1_errors:
            return "FAILED"
        elif self.has_warnings:
            return "PASSED (with warnings)"
        return "PASSED"

    def add_issue(
        self,
        code: str,
        file_path: Optional[Path] = None,
        line: Optional[int] = None,
        context: str = "",
        tier: ValidationTier = ValidationTier.TIER1,
    ) -> None:
        """
        Add a validation issue.

        Args:
            code: Error code
            file_path: Source file path
            line: Line number
            context: Additional context
            tier: Validation tier
        """
        issue = ValidationIssue.from_code(
            code=code,
            file_path=file_path,
            line=line,
            context=context,
            tier=tier,
        )
        if tier == ValidationTier.TIER1:
            self.tier1_issues.append(issue)
        else:
            self.tier2_issues.append(issue)

    def add_pass(self, message: str) -> None:
        """Add a passing check message."""
        self.passes.append(message)

    def merge(self, other: "UnifiedValidationResult") -> None:
        """
        Merge another result into this one.

        Args:
            other: Result to merge
        """
        self.tier1_issues.extend(other.tier1_issues)
        self.tier2_issues.extend(other.tier2_issues)
        self.passes.extend(other.passes)
        self.checks_run.extend(other.checks_run)
        self.metadata.update(other.metadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "path": str(self.doc_path),
            "status": self.status,
            "exit_code": self.exit_code(),
            "tier1": {
                "errors": len(self.tier1_errors),
                "warnings": len(self.tier1_warnings),
                "issues": [
                    {
                        "code": i.code,
                        "message": i.message,
                        "severity": i.severity.value,
                        "file": str(i.file_path) if i.file_path else None,
                        "line": i.line,
                        "context": i.context,
                    }
                    for i in self.tier1_issues
                ],
            },
            "tier2": {
                "errors": len(self.tier2_errors),
                "warnings": len(self.tier2_warnings),
                "issues": [
                    {
                        "code": i.code,
                        "message": i.message,
                        "severity": i.severity.value,
                        "file": str(i.file_path) if i.file_path else None,
                        "line": i.line,
                        "context": i.context,
                    }
                    for i in self.tier2_issues
                ],
            },
            "passes": self.passes,
            "checks_run": self.checks_run,
            "metadata": self.metadata,
        }

    def format_text(self, verbose: bool = False) -> str:
        """
        Format result as text output.

        Args:
            verbose: Include all passes

        Returns:
            Formatted text string
        """
        lines = [
            "=" * 50,
            "UCX Validation Result",
            "=" * 50,
            f"Path: {self.doc_path}",
            f"Status: {self.status}",
            "",
        ]

        # Tier 1 section
        lines.append("[TIER 1: CORE CHECKS]")
        lines.append("")

        if self.tier1_issues:
            for issue in self.tier1_issues:
                lines.append(issue.format())
        else:
            lines.append("[PASS] All Tier 1 checks passed")

        lines.append("")

        # Tier 2 section
        lines.append("[TIER 2: ADVISORY CHECKS]")
        lines.append("")

        if self.tier2_issues:
            for issue in self.tier2_issues:
                lines.append(issue.format())
        else:
            lines.append("[PASS] All Tier 2 checks passed")

        lines.append("")

        # Summary
        lines.append("=" * 50)
        lines.append("Summary")
        lines.append("=" * 50)
        lines.append(f"Tier 1 Errors:   {len(self.tier1_errors)}")
        lines.append(f"Tier 1 Warnings: {len(self.tier1_warnings)}")
        lines.append(f"Tier 2 Warnings: {len(self.tier2_warnings)}")
        lines.append(f"Checks Run:      {len(self.checks_run)}")
        lines.append(f"Status: {self.status}")

        if verbose and self.passes:
            lines.append("")
            lines.append("Passes:")
            for p in self.passes:
                lines.append(f"  [PASS] {p}")

        return "\n".join(lines)
