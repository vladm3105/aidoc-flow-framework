"""BRD (Business Requirements Document) validator.

This module provides registry-compatible BRD validation by delegating to
UnifiedBRDValidator (ucx.validators.brd package).

Version: 1.9.2
"""

from pathlib import Path

from ucx.models.enums import DocType, ValidationStatus
from ucx.models.review import ValidationResult
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator
from ucx.validators.brd import UnifiedBRDValidator


@register_validator(DocType.BRD)
class BRDValidator(BaseValidator):
    """
    Validator for Business Requirements Documents (Layer 1).

    This class wraps UnifiedBRDValidator to provide compatibility with the
    validator registry. All validation logic is delegated to UnifiedBRDValidator.
    """

    def __init__(self, tier1_only: bool = False):
        """
        Initialize BRD validator.

        Args:
            tier1_only: If True, run only Tier 1 (blocking) checks
        """
        super().__init__()
        self.tier1_only = tier1_only
        self._unified_validator = UnifiedBRDValidator()

    def validate(self, doc_path: Path) -> ValidationResult:
        """
        Validate a BRD document using UnifiedBRDValidator.

        Args:
            doc_path: Path to document file or directory

        Returns:
            ValidationResult with errors, warnings, passes
        """
        # Reset state
        self.errors = []
        self.warnings = []
        self.passes = []

        # Delegate to UnifiedBRDValidator
        unified_result = self._unified_validator.validate(
            doc_path,
            tier1_only=self.tier1_only,
        )

        # Convert UnifiedValidationResult to ValidationResult
        # Tier 1 issues are errors
        for issue in unified_result.tier1_issues:
            msg = f"{issue.file_path.name}:{issue.line or 0}: [{issue.code}] {issue.message}"
            if issue.context:
                msg += f" ({issue.context})"
            self.errors.append(msg)

        # Tier 2 issues are warnings
        for issue in unified_result.tier2_issues:
            msg = f"{issue.file_path.name}:{issue.line or 0}: [{issue.code}] {issue.message}"
            if issue.context:
                msg += f" ({issue.context})"
            self.warnings.append(msg)

        # Convert passes
        for pass_msg in unified_result.passes:
            self.passes.append(pass_msg)

        # Determine status based on Tier 1 errors only
        if unified_result.has_tier1_errors:
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
        """
        Validate a single file (not used - validation delegated to UnifiedBRDValidator).

        This method exists only to satisfy the abstract base class requirement.
        """
        pass
