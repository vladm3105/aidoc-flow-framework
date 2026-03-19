"""PRD (Product Requirements Document) validator.

Wrapper that integrates UnifiedPRDValidator with the BaseValidator interface.
Provides both the legacy interface and access to advanced features.
"""

from pathlib import Path

from ucx.models.enums import DocType
from ucx.models.review import ValidationResult
from ucx.models.enums import ValidationStatus
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.PRD)
class PRDValidator(BaseValidator):
    """Validator for Product Requirements Documents (Layer 2).

    This is a wrapper that provides backward compatibility with BaseValidator
    while leveraging the comprehensive UnifiedPRDValidator internally.
    """

    def __init__(
        self,
        strict: bool = False,
        profile: str = "mvp",
        tier1_only: bool = False,
    ):
        """Initialize PRD validator.

        Args:
            strict: Treat warnings as errors
            profile: Template profile ('mvp' or 'standard')
            tier1_only: Only run Tier 1 (blocking) checks
        """
        super().__init__()
        self.strict = strict
        self.profile = profile
        self.tier1_only = tier1_only

        # Advanced result storage
        self._unified_result = None

    def validate(self, doc_path: Path) -> ValidationResult:
        """Validate a PRD document using UnifiedPRDValidator.

        Args:
            doc_path: Path to document file or directory

        Returns:
            ValidationResult with errors, warnings, passes
        """
        # Reset state
        self.errors = []
        self.warnings = []
        self.passes = []

        try:
            # Use unified validator
            from ucx.validators.prd import UnifiedPRDValidator

            validator = UnifiedPRDValidator(
                strict=self.strict,
                verbose=False,
                profile=self.profile,
            )

            self._unified_result = validator.validate(doc_path, tier1_only=self.tier1_only)

            # Convert to BaseValidator format
            for issue in self._unified_result.tier1_issues:
                self.errors.append(f"[{issue.code}] {issue.file}: {issue.message}")

            for issue in self._unified_result.tier2_issues:
                self.warnings.append(f"[{issue.code}] {issue.file}: {issue.message}")

            # Add score information as passes
            self.passes.append(
                f"SYS-Ready Score: {self._unified_result.sys_ready_score:.1f}% "
                f"({'PASS' if self._unified_result.sys_passed else 'FAIL'})"
            )
            self.passes.append(
                f"EARS-Ready Score: {self._unified_result.ears_ready_score:.1f}% "
                f"({'PASS' if self._unified_result.ears_passed else 'FAIL'})"
            )
            self.passes.append(f"Files validated: {len(self._unified_result.files_validated)}")

        except ImportError:
            # Fallback to basic validation if UnifiedPRDValidator not available
            return self._fallback_validate(doc_path)

        # Determine status
        if self.errors:
            status = ValidationStatus.FAILED
        elif self.strict and self.warnings:
            status = ValidationStatus.FAILED
        else:
            status = ValidationStatus.PASSED

        return ValidationResult(
            status=status,
            errors=self.errors,
            warnings=self.warnings,
            passes=self.passes,
        )

    def _fallback_validate(self, doc_path: Path) -> ValidationResult:
        """Fallback to basic validation if unified validator unavailable."""
        files = self._get_files(doc_path)

        for file_path in files:
            content = file_path.read_text(encoding="utf-8")
            self._validate_file(file_path, content)

        if self.errors:
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
        """Basic file validation (fallback only)."""
        file_name = file_path.name

        # Check YAML frontmatter
        self.check_yaml_frontmatter(
            content,
            ["title", "doc_id", "version", "status"],
            file_name,
        )

        # Check element IDs
        id_count = self.check_element_ids(
            content,
            r"PRD\.\d{2}\.\d{2}\.\d{2}",
            file_name,
        )
        if id_count == 0:
            self.warnings.append(f"{file_name}: No PRD element IDs found")

        # Check traceability to BRD
        self.check_traceability(
            content,
            [r"@brd:", r"@ears:"],
            file_name,
        )

    @property
    def unified_result(self):
        """Access the full UnifiedPRDValidator result.

        Returns detailed information including:
        - tier1_issues, tier2_issues
        - sys_ready_score, ears_ready_score
        - files_validated
        - format_text(), format_report() methods
        """
        return self._unified_result

    @property
    def sys_ready_score(self) -> float:
        """Get SYS-Ready score."""
        if self._unified_result:
            return self._unified_result.sys_ready_score
        return 0.0

    @property
    def ears_ready_score(self) -> float:
        """Get EARS-Ready score."""
        if self._unified_result:
            return self._unified_result.ears_ready_score
        return 0.0

    @property
    def scores_passed(self) -> bool:
        """Check if both readiness scores pass threshold."""
        if self._unified_result:
            return self._unified_result.both_passed
        return False
