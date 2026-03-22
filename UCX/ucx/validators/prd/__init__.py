"""Unified PRD Validator for UCX Framework v1.20.0.

This module provides comprehensive validation for Product Requirements Documents (PRD)
following the 21-section MVP template structure with dual readiness scoring.

Key Features:
- 21-section structure validation
- Section 10 (Customer-Facing Content) blocking enforcement
- Section 8 layer separation note validation
- 13 element type code validation (PRD.NN.TT.SS format)
- Dual scoring: SYS-Ready + EARS-Ready
- Forward reference blocking for Layer 5+ artifacts
- Auto-fixer with UCX-ACTION output

Usage:
    from ucx.validators.prd import UnifiedPRDValidator

    validator = UnifiedPRDValidator()
    result = validator.validate(Path("docs/02_PRD/PRD-01/"), tier1_only=True)
    print(result.format_text())
"""

from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import re

from ucx.models.enums import DocType, ValidationStatus
from ucx.models.review import ValidationResult
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


class Tier(Enum):
    """Validation tier classification for PRD."""
    TIER1 = "tier1"  # Blocking errors
    TIER2 = "tier2"  # Advisory warnings


@dataclass
class ValidationIssue:
    """Individual validation issue for PRD.

    Simplified issue class for PRD validation that doesn't require
    the full error_codes infrastructure.
    """

    code: str
    message: str
    file: str = ""
    line: Optional[int] = None
    tier: Tier = Tier.TIER1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "tier": self.tier.value,
        }

    def format(self) -> str:
        """Format issue for display."""
        location = f"{self.file}" if self.file else ""
        if self.line:
            location += f":{self.line}"
        tier_label = "[ERROR]" if self.tier == Tier.TIER1 else "[WARN]"
        return f"{tier_label} {self.code}: {location} {self.message}"


@dataclass
class PRDValidationResult:
    """Result of PRD validation."""

    tier1_issues: List[ValidationIssue] = field(default_factory=list)
    tier2_issues: List[ValidationIssue] = field(default_factory=list)
    sys_ready_score: float = 0.0
    ears_ready_score: float = 0.0
    template_profile: str = "mvp"
    threshold: int = 85
    files_validated: List[str] = field(default_factory=list)
    checks_run: List[str] = field(default_factory=list)
    validation_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def has_errors(self) -> bool:
        """Check if any Tier 1 (blocking) errors exist."""
        return len(self.tier1_issues) > 0

    @property
    def errors(self) -> List[ValidationIssue]:
        """Get all Tier 1 errors."""
        return self.tier1_issues

    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get all Tier 2 warnings."""
        return self.tier2_issues

    @property
    def sys_passed(self) -> bool:
        """Check if SYS-Ready score meets threshold."""
        return self.sys_ready_score >= self.threshold

    @property
    def ears_passed(self) -> bool:
        """Check if EARS-Ready score meets threshold."""
        return self.ears_ready_score >= self.threshold

    @property
    def both_passed(self) -> bool:
        """Check if both scores pass."""
        return self.sys_passed and self.ears_passed

    def exit_code(self, strict: bool = False) -> int:
        """Calculate exit code based on results."""
        if self.has_errors:
            return 2
        if self.tier2_issues and strict:
            return 2
        if self.tier2_issues:
            return 1
        return 0

    def format_text(self, verbose: bool = False) -> str:
        """Format result as text output."""
        lines = []
        lines.append(f"PRD Validation Results ({self.template_profile} profile)")
        lines.append("=" * 60)
        lines.append(f"Files validated: {len(self.files_validated)}")
        lines.append(f"Tier 1 issues: {len(self.tier1_issues)}")
        lines.append(f"Tier 2 issues: {len(self.tier2_issues)}")
        lines.append("")
        lines.append("Readiness Scores:")
        sys_icon = "✓" if self.sys_passed else "✗"
        ears_icon = "✓" if self.ears_passed else "✗"
        lines.append(f"  SYS-Ready:  {sys_icon} {self.sys_ready_score:.1f}% (target: ≥{self.threshold}%)")
        lines.append(f"  EARS-Ready: {ears_icon} {self.ears_ready_score:.1f}% (target: ≥{self.threshold}%)")

        if self.tier1_issues:
            lines.append("")
            lines.append("Tier 1 Issues (Blocking):")
            for issue in self.tier1_issues[:20]:
                lines.append(f"  [{issue.code}] {issue.file}: {issue.message}")
            if len(self.tier1_issues) > 20:
                lines.append(f"  ... and {len(self.tier1_issues) - 20} more")

        if verbose and self.tier2_issues:
            lines.append("")
            lines.append("Tier 2 Issues (Advisory):")
            for issue in self.tier2_issues[:20]:
                lines.append(f"  [{issue.code}] {issue.file}: {issue.message}")
            if len(self.tier2_issues) > 20:
                lines.append(f"  ... and {len(self.tier2_issues) - 20} more")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "tier1_issues": [i.to_dict() for i in self.tier1_issues],
            "tier2_issues": [i.to_dict() for i in self.tier2_issues],
            "sys_ready_score": self.sys_ready_score,
            "ears_ready_score": self.ears_ready_score,
            "template_profile": self.template_profile,
            "threshold": self.threshold,
            "files_validated": self.files_validated,
            "checks_run": self.checks_run,
            "validation_time": self.validation_time,
            "has_errors": self.has_errors,
            "sys_passed": self.sys_passed,
            "ears_passed": self.ears_passed,
        }

    def format_report(self, doc_id: str, doc_type: str = "PRD", version: int = 1) -> str:
        """Format result as SDD-compliant validation report."""
        lines = []
        lines.append("---")
        lines.append(f'title: "UCX Validate Report: {doc_type}"')
        lines.append("tags:")
        lines.append("  - ucx-validate")
        lines.append("  - prd-validate")
        lines.append("  - layer-2-artifact")
        lines.append("custom_fields:")
        lines.append("  document_type: ucx-validate-report")
        lines.append(f"  source_artifact_type: {doc_type}")
        lines.append(f'  validate_id: "UCX-{doc_id}-validate-v{version:03d}"')
        lines.append("  layer: 2")
        lines.append(f"  total_errors: {len(self.tier1_issues)}")
        lines.append(f"  total_warnings: {len(self.tier2_issues)}")
        lines.append(f"  sys_ready_score: {self.sys_ready_score:.1f}")
        lines.append(f"  ears_ready_score: {self.ears_ready_score:.1f}")
        lines.append(f'  last_updated: "{self.validation_time}"')
        lines.append(f"  tier1_errors: {len(self.tier1_issues)}")
        lines.append("  tier1_warnings: 0")
        lines.append(f"  tier2_warnings: {len(self.tier2_issues)}")
        lines.append(f"  checks_run: {len(self.checks_run)}")
        lines.append("---")
        lines.append("")
        lines.append(f"# UCX Validate Report: {doc_id}")
        lines.append("")
        lines.append("## 0. Document Control")
        lines.append("")
        lines.append("| Item | Details |")
        lines.append("|------|---------|")
        lines.append(f"| **Validated Document** | {doc_id} |")
        lines.append(f"| **Validate ID** | UCX-{doc_id}-validate-v{version:03d} |")
        lines.append(f"| **Validate Date** | {self.validation_time} |")
        status = "✅ PASS" if not self.has_errors else "❌ FAIL"
        lines.append(f"| **Status** | {status} |")
        lines.append("")
        lines.append("## 1. Readiness Scores")
        lines.append("")
        lines.append("| Score | Value | Target | Status |")
        lines.append("|-------|-------|--------|--------|")
        sys_status = "✅ PASS" if self.sys_passed else "⚠️ REVIEW"
        ears_status = "✅ PASS" if self.ears_passed else "⚠️ REVIEW"
        lines.append(f"| **SYS-Ready** | {self.sys_ready_score:.1f}% | ≥{self.threshold}% | {sys_status} |")
        lines.append(f"| **EARS-Ready** | {self.ears_ready_score:.1f}% | ≥{self.threshold}% | {ears_status} |")
        lines.append("")
        lines.append(f"## 2. Errors ({len(self.tier1_issues)})")
        lines.append("")
        if self.tier1_issues:
            lines.append("| Code | File | Message |")
            lines.append("|------|------|---------|")
            for issue in self.tier1_issues:
                lines.append(f"| {issue.code} | {issue.file} | {issue.message} |")
        else:
            lines.append("*No blocking errors found.*")
        lines.append("")
        lines.append(f"## 3. Warnings ({len(self.tier2_issues)})")
        lines.append("")
        if self.tier2_issues:
            lines.append("| Code | File | Message |")
            lines.append("|------|------|---------|")
            for issue in self.tier2_issues[:50]:
                lines.append(f"| {issue.code} | {issue.file} | {issue.message} |")
            if len(self.tier2_issues) > 50:
                lines.append(f"| ... | ... | {len(self.tier2_issues) - 50} more warnings |")
        else:
            lines.append("*No warnings found.*")
        lines.append("")
        lines.append("## 4. Next Steps")
        lines.append("")
        if self.has_errors:
            lines.append("- [ ] Fix all Tier 1 errors before proceeding")
            lines.append("- [ ] Run `ucx validate prd` again to verify fixes")
        else:
            lines.append("- [ ] Address warnings if applicable")
            lines.append("- [ ] Run `ucx review prd` for AI review")
        return "\n".join(lines)


@register_validator(DocType.PRD)
class PRDValidator(BaseValidator):
    """Registry-facing PRD validator backed by UnifiedPRDValidator."""

    def __init__(
        self,
        strict: bool = False,
        profile: str = "mvp",
        tier1_only: bool = False,
    ):
        super().__init__()
        self.strict = strict
        self.profile = profile
        self.tier1_only = tier1_only
        self._unified_result: Optional[PRDValidationResult] = None

    def validate(self, doc_path: Path) -> ValidationResult:
        self.errors = []
        self.warnings = []
        self.passes = []

        validator = UnifiedPRDValidator(
            strict=self.strict,
            verbose=False,
            profile=self.profile,
        )
        self._unified_result = validator.validate(doc_path, tier1_only=self.tier1_only)

        for issue in self._unified_result.tier1_issues:
            self.errors.append(f"[{issue.code}] {issue.file}: {issue.message}")

        for issue in self._unified_result.tier2_issues:
            self.warnings.append(f"[{issue.code}] {issue.file}: {issue.message}")

        self.passes.append(
            f"SYS-Ready Score: {self._unified_result.sys_ready_score:.1f}% "
            f"({'PASS' if self._unified_result.sys_passed else 'FAIL'})"
        )
        self.passes.append(
            f"EARS-Ready Score: {self._unified_result.ears_ready_score:.1f}% "
            f"({'PASS' if self._unified_result.ears_passed else 'FAIL'})"
        )
        self.passes.append(f"Files validated: {len(self._unified_result.files_validated)}")

        if self.errors or (self.strict and self.warnings):
            status = ValidationStatus.FAILED
        else:
            status = ValidationStatus.PASSED

        return ValidationResult(
            status=status,
            errors=self.errors,
            warnings=self.warnings,
            passes=self.passes,
        )

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Required by BaseValidator; not used because validate() is overridden."""
        return

    @property
    def unified_result(self) -> Optional[PRDValidationResult]:
        return self._unified_result

class UnifiedPRDValidator:
    """Unified validator for PRD documents.

    Implements 21-section structure validation with dual scoring
    and forward reference blocking.
    """

    def __init__(
        self,
        strict: bool = False,
        verbose: bool = False,
        profile: str = "mvp",
    ):
        """Initialize PRD validator.

        Args:
            strict: Treat warnings as errors
            verbose: Enable verbose output
            profile: Template profile (mvp or standard)
        """
        self.strict = strict
        self.verbose = verbose
        self.profile = profile
        self.threshold = 85 if profile == "mvp" else 90

    def validate(
        self,
        path: Union[str, Path],
        tier1_only: bool = False,
    ) -> PRDValidationResult:
        """Validate a PRD document or directory.

        Args:
            path: Path to PRD file or directory
            tier1_only: Only run Tier 1 (blocking) checks

        Returns:
            PRDValidationResult with all findings and scores
        """
        path = Path(path)
        result = PRDValidationResult(template_profile=self.profile, threshold=self.threshold)
        from ucx.validators.common.file_utils import is_companion_report

        # Collect files to validate
        if path.is_dir():
            files = sorted(path.glob("*.md"))
            # Exclude index/templates and companion reports (validation/review/remediation files).
            files = [
                f for f in files
                if not f.name.startswith("PRD-00") and not is_companion_report(f)
            ]
        else:
            files = [path]

        result.files_validated = [str(f) for f in files]

        # Aggregate content for scoring
        all_content = ""

        for file_path in files:
            content = file_path.read_text(encoding="utf-8")
            all_content += content + "\n"

            # Run file-level validation
            self._validate_file(file_path, content, result, tier1_only)

        # Keep report metadata consistent with BRD validator conventions.
        result.checks_run = [
            "structure",
            "metadata",
            "element_codes",
            "quality_gate_tier1",
            "scoring",
        ]
        if not tier1_only:
            result.checks_run.append("quality_gate_tier2")

        # Run corpus-level checks if multi-file
        if len(files) > 1:
            self._validate_corpus(path, files, result, tier1_only)

        # Calculate scores
        self._calculate_scores(all_content, result)

        return result

    def _validate_file(
        self,
        file_path: Path,
        content: str,
        result: PRDValidationResult,
        tier1_only: bool,
    ) -> None:
        """Run file-level validation checks."""
        from ucx.validators.prd.structure import validate_structure
        from ucx.validators.prd.metadata import validate_metadata
        from ucx.validators.prd.element_codes import validate_element_codes
        from ucx.validators.prd.quality_gate import run_quality_gates

        # Validate captured LLM payloads only when audit capture is present.
        llm_issues = self._validate_llm_response_capture(file_path, content)
        for issue in llm_issues:
            if issue.tier == Tier.TIER1:
                result.tier1_issues.append(issue)
            elif not tier1_only:
                result.tier2_issues.append(issue)

        # Structure validation
        structure_issues = validate_structure(file_path, content)
        for issue in structure_issues:
            if issue.tier == Tier.TIER1:
                result.tier1_issues.append(issue)
            elif not tier1_only:
                result.tier2_issues.append(issue)

        # Metadata validation
        metadata_issues = validate_metadata(file_path, content)
        for issue in metadata_issues:
            if issue.tier == Tier.TIER1:
                result.tier1_issues.append(issue)
            elif not tier1_only:
                result.tier2_issues.append(issue)

        # Element code validation
        element_issues = validate_element_codes(file_path, content)
        for issue in element_issues:
            if issue.tier == Tier.TIER1:
                result.tier1_issues.append(issue)
            elif not tier1_only:
                result.tier2_issues.append(issue)

        # Quality gate checks
        gate_issues = run_quality_gates(file_path, content, tier1_only)
        for issue in gate_issues:
            if issue.tier == Tier.TIER1:
                result.tier1_issues.append(issue)
            else:
                result.tier2_issues.append(issue)

    def _validate_llm_response_capture(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate embedded raw LLM responses captured during PRD creation."""
        issues: List[ValidationIssue] = []

        if "UCX_LLM_RESPONSE_CAPTURE:BEGIN" not in content:
            # Audit capture is optional; when omitted, skip this validation track.
            return issues

        if "UCX_LLM_RESPONSE_CAPTURE:END" not in content:
            issues.append(ValidationIssue(
                code="PRD-E023",
                message="UCX LLM response audit block is incomplete (missing END marker)",
                file=file_path.name,
                tier=Tier.TIER1,
            ))
            return issues

        meta_match = re.search(r"<!--\s*UCX_LLM_META:\s*(\{.*?\})\s*-->", content, re.DOTALL)
        fallback_used = False
        if meta_match:
            try:
                meta = json.loads(meta_match.group(1))
                fallback_used = bool(meta.get("fallback_used", False))
            except Exception:
                issues.append(ValidationIssue(
                    code="PRD-W022",
                    message="Unable to parse UCX_LLM_META JSON payload",
                    file=file_path.name,
                    tier=Tier.TIER2,
                ))

        raw_attempts = re.findall(
            r"<pre\s+data-ucx-llm-attempt=\"\d+\">(.*?)</pre>",
            content,
            re.DOTALL,
        )

        if not raw_attempts:
            issues.append(ValidationIssue(
                code="PRD-E023",
                message="No raw LLM attempt payloads found inside UCX response audit block",
                file=file_path.name,
                tier=Tier.TIER1,
            ))
            return issues

        invalid_attempts = 0
        for raw in raw_attempts:
            decoded = (
                raw.replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&amp;", "&")
                .replace("&quot;", '"')
                .replace("&#x27;", "'")
            )
            lowered = decoded.lower()
            looks_like_summary = bool(re.search(r"\bi\s+have\s+created\s+the\s+prd\b", lowered))
            looks_like_template = (
                "[mvp product/feature name]" in lowered
                or "prd.nn." in lowered
                or "yyyy-mm-ddthh:mm:ss" in lowered
            )
            looks_like_structured_prd = bool(
                re.search(r"(?m)^#\s+PRD-\d{2,9}:", decoded)
                and re.search(r"(?im)^##\s+1\.\s+Document\s+Control", decoded)
            )
            if looks_like_summary or looks_like_template or not looks_like_structured_prd:
                invalid_attempts += 1

        if invalid_attempts == len(raw_attempts):
            issues.append(ValidationIssue(
                code="PRD-E024",
                message=(
                    "All captured LLM responses are invalid/template-like; "
                    "PRD generation output requires investigation"
                ),
                file=file_path.name,
                tier=Tier.TIER1,
            ))

        if fallback_used:
            issues.append(ValidationIssue(
                code="PRD-W023",
                message="UCX deterministic template fallback was used because LLM response quality failed",
                file=file_path.name,
                tier=Tier.TIER2,
            ))

        return issues

    def _validate_corpus(
        self,
        corpus_path: Path,
        files: List[Path],
        result: PRDValidationResult,
        tier1_only: bool,
    ) -> None:
        """Run corpus-level validation checks."""
        from ucx.validators.prd.corpus_gate import run_corpus_checks

        corpus_issues = run_corpus_checks(corpus_path, files, tier1_only)
        for issue in corpus_issues:
            if issue.tier == Tier.TIER1:
                result.tier1_issues.append(issue)
            else:
                result.tier2_issues.append(issue)

    def _calculate_scores(self, content: str, result: PRDValidationResult) -> None:
        """Calculate SYS-Ready and EARS-Ready scores."""
        from ucx.validators.prd.scoring import PRDScorer

        scorer = PRDScorer(profile=self.profile)
        scores = scorer.calculate(content)

        result.sys_ready_score = scores.sys_ready
        result.ears_ready_score = scores.ears_ready

        # Add score-based issues if below threshold
        if not scores.sys_passed:
            result.tier1_issues.append(ValidationIssue(
                code="PRD-E015",
                message=f"SYS-Ready score {scores.sys_ready:.1f}% below threshold {self.threshold}%",
                file="corpus",
                tier=Tier.TIER1,
            ))

        if not scores.ears_passed:
            result.tier1_issues.append(ValidationIssue(
                code="PRD-E016",
                message=f"EARS-Ready score {scores.ears_ready:.1f}% below threshold {self.threshold}%",
                file="corpus",
                tier=Tier.TIER1,
            ))


# Export for external use
__all__ = ["UnifiedPRDValidator", "PRDValidationResult", "ValidationIssue", "Tier"]
