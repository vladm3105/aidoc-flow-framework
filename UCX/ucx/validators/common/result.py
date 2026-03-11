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
        Format result as text output (legacy format).

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

    def format_report(self, doc_id: str, doc_type: str = "BRD", version: int = 1) -> str:
        """
        Format result as SDD-compliant validation report with YAML frontmatter.

        Args:
            doc_id: Document ID (e.g., 'BRD-01')
            doc_type: Document type (e.g., 'BRD', 'PRD')
            version: Report version number

        Returns:
            SDD-compliant markdown report
        """
        from datetime import datetime

        from ucx.version import __version__

        now = datetime.now()
        validation_date = now.strftime("%Y-%m-%dT%H:%M:%S")
        report_id = f"VAL-{doc_type.upper()}-{doc_id.split('-')[-1]}-v{version:03d}"

        # Calculate validation score (100 - penalty)
        # Each Tier 1 error = -2 points, Tier 1 warning = -1, Tier 2 warning = -0.5
        score = 100.0
        score -= len(self.tier1_errors) * 2
        score -= len(self.tier1_warnings) * 1
        score -= len(self.tier2_warnings) * 0.5
        score = max(0, score)  # Don't go negative

        status_emoji = "✅" if self.is_valid else "❌"
        status_text = "PASS" if self.is_valid else "FAIL"

        lines = []

        # YAML Frontmatter
        lines.append("---")
        lines.append(f"doc_id: {doc_id}.V")
        lines.append(f'title: "{doc_id} Validation Report - Structural Quality Check"')
        lines.append(f"report_version: v{version:03d}")
        lines.append(f"validation_date: {validation_date}")
        lines.append(f"validator: UCX Framework v{__version__}")
        lines.append("tags:")
        lines.append("  - validation-report")
        lines.append(f"  - {doc_type.lower()}-quality")
        lines.append("  - structural-validation")
        lines.append("  - quality-assurance")
        lines.append("custom_fields:")
        lines.append("  artifact_type: VALIDATION")
        lines.append(f"  validated_document: {doc_id}")
        lines.append(f"  validation_score: {score:.1f}")
        lines.append(f"  status: {status_text}")
        lines.append(f"  tier1_errors: {len(self.tier1_errors)}")
        lines.append(f"  tier1_warnings: {len(self.tier1_warnings)}")
        lines.append(f"  tier2_warnings: {len(self.tier2_warnings)}")
        lines.append(f"  checks_run: {len(self.checks_run)}")
        lines.append("---")
        lines.append("")

        # Document Title
        lines.append(f"# {doc_id} Validation Report v{version:03d}")
        lines.append("")

        # Document Control
        lines.append("## 0. Document Control")
        lines.append("")
        lines.append("| Item | Details |")
        lines.append("|------|---------|")
        lines.append(f"| **Source Document** | {doc_id} |")
        lines.append(f"| **Report ID** | {report_id} |")
        lines.append(f"| **Validation Date** | {validation_date} |")
        lines.append(f"| **Validation Method** | UCX Unified Validator (Tier 1 + Tier 2) |")
        lines.append(f"| **Validator Version** | UCX Framework v{__version__} |")
        lines.append(f"| **Checks Run** | {len(self.checks_run)} |")
        lines.append(f"| **Status** | {status_text} {status_emoji} |")
        lines.append(f"| **Validation Score** | {score:.1f}/100 |")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary
        lines.append("## 1. Executive Summary")
        lines.append("")
        lines.append(f"**Document**: {doc_id}")
        lines.append(f"**Path**: `{self.doc_path}`")
        lines.append(f"**Validation Date**: {validation_date}")
        lines.append(f"**Overall Score**: **{score:.1f}/100** {status_emoji} {status_text}")
        lines.append("")

        if self.is_valid:
            lines.append("The document passes all Tier 1 (blocking) structural checks.")
        else:
            lines.append(f"The document has **{len(self.tier1_errors)} Tier 1 errors** that must be resolved before proceeding.")

        if self.tier2_warnings:
            lines.append(f"There are also **{len(self.tier2_warnings)} Tier 2 advisory warnings** for consideration.")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Score Breakdown
        lines.append("## 2. Validation Score Breakdown")
        lines.append("")
        lines.append("| Category | Count | Penalty | Notes |")
        lines.append("|----------|-------|---------|-------|")
        lines.append(f"| Tier 1 Errors | {len(self.tier1_errors)} | -{len(self.tier1_errors) * 2} pts | Blocking issues |")
        lines.append(f"| Tier 1 Warnings | {len(self.tier1_warnings)} | -{len(self.tier1_warnings) * 1} pts | Core check warnings |")
        lines.append(f"| Tier 2 Warnings | {len(self.tier2_warnings)} | -{len(self.tier2_warnings) * 0.5:.1f} pts | Advisory issues |")
        lines.append(f"| **Total Score** | | **{score:.1f}/100** | {status_text} |")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Tier 1 Findings
        lines.append("## 3. Tier 1 Findings (Core Checks)")
        lines.append("")
        lines.append("Tier 1 checks are **blocking** and must be resolved before downstream processing.")
        lines.append("")

        if self.tier1_errors:
            lines.append("### 3.1 Errors")
            lines.append("")
            lines.append("| # | Code | File | Line | Issue | Remediation |")
            lines.append("|---|------|------|------|-------|-------------|")
            for i, issue in enumerate(self.tier1_errors, 1):
                file_str = str(issue.file_path.name) if issue.file_path else "-"
                line_str = str(issue.line) if issue.line else "-"
                error = get_error(issue.code)
                remediation = error.remediation if error else "See documentation"
                context = (issue.context[:80] + "..." if len(issue.context) > 80 else issue.context).replace("|", "\\|")
                lines.append(f"| {i} | `{issue.code}` | `{file_str}` | {line_str} | {context} | {remediation} |")
            lines.append("")
        else:
            lines.append("### 3.1 Errors")
            lines.append("")
            lines.append("✅ No Tier 1 errors found.")
            lines.append("")

        if self.tier1_warnings:
            lines.append("### 3.2 Warnings")
            lines.append("")
            lines.append("| # | Code | File | Line | Issue | Remediation |")
            lines.append("|---|------|------|------|-------|-------------|")
            for i, issue in enumerate(self.tier1_warnings, 1):
                file_str = str(issue.file_path.name) if issue.file_path else "-"
                line_str = str(issue.line) if issue.line else "-"
                error = get_error(issue.code)
                remediation = error.remediation if error else "See documentation"
                context = (issue.context[:80] + "..." if len(issue.context) > 80 else issue.context).replace("|", "\\|")
                lines.append(f"| {i} | `{issue.code}` | `{file_str}` | {line_str} | {context} | {remediation} |")
            lines.append("")
        else:
            lines.append("### 3.2 Warnings")
            lines.append("")
            lines.append("✅ No Tier 1 warnings found.")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Tier 2 Findings
        lines.append("## 4. Tier 2 Findings (Advisory Checks)")
        lines.append("")
        lines.append("Tier 2 checks are **advisory** and represent best practices or minor improvements.")
        lines.append("")

        if self.tier2_warnings:
            lines.append("### 4.1 Warnings")
            lines.append("")
            lines.append("| # | Code | File | Line | Issue | Remediation |")
            lines.append("|---|------|------|------|-------|-------------|")
            for i, issue in enumerate(self.tier2_warnings, 1):
                file_str = str(issue.file_path.name) if issue.file_path else "-"
                line_str = str(issue.line) if issue.line else "-"
                error = get_error(issue.code)
                remediation = error.remediation if error else "See documentation"
                context = (issue.context[:80] + "..." if len(issue.context) > 80 else issue.context).replace("|", "\\|")
                lines.append(f"| {i} | `{issue.code}` | `{file_str}` | {line_str} | {context} | {remediation} |")
            lines.append("")
        else:
            lines.append("✅ No Tier 2 warnings found.")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Checks Run
        lines.append("## 5. Checks Performed")
        lines.append("")
        lines.append("| # | Check | Status |")
        lines.append("|---|-------|--------|")
        for i, check in enumerate(self.checks_run, 1):
            lines.append(f"| {i} | {check} | ✅ Completed |")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Next Steps
        lines.append("## 6. Recommended Next Steps")
        lines.append("")
        if self.tier1_errors:
            lines.append("1. **Resolve Tier 1 Errors** - These are blocking issues that prevent downstream processing")
            lines.append("2. **Re-run Validation** - Use `ucx validate` to verify fixes")
            lines.append("3. **Address Tier 2 Warnings** - Optional but recommended for quality")
        elif self.tier2_warnings:
            lines.append("1. **Review Tier 2 Warnings** - Consider addressing advisory issues")
            lines.append("2. **Proceed to AI Review** - Use `ucx review` for content analysis")
        else:
            lines.append("1. **Proceed to AI Review** - Use `ucx review` for comprehensive content analysis")
            lines.append("2. **Generate Downstream Artifacts** - Document is ready for PRD generation")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Footer
        lines.append("*Generated by UCX Framework v" + __version__ + "*")
        lines.append("")

        return "\n".join(lines)
