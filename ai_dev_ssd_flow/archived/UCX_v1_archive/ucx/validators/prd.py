"""PRD (Product Requirements Document) validator.

Wrapper that integrates UnifiedPRDValidator with the BaseValidator interface.
Provides both the legacy interface and access to advanced features.
"""

from pathlib import Path
import re

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
            from ucx.validators.prd.__init__ import UnifiedPRDValidator

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

        # Enforce document ID consistency (filename/frontmatter/H1/Document Control).
        filename_id = self._extract_filename_doc_id(file_path)
        frontmatter_id = self._extract_frontmatter_doc_id(content)
        h1_id = self._extract_h1_doc_id(content)
        section_id = self._extract_doc_control_doc_id(content)

        ids = {
            "filename": filename_id,
            "frontmatter": frontmatter_id,
            "h1": h1_id,
            "document_control": section_id,
        }
        present = {v for v in ids.values() if v}
        if len(present) > 1:
            self.errors.append(f"[{file_name}] PRD-E001: Inconsistent PRD ID across filename/frontmatter/H1/Document Control: {ids}")

        canonical = filename_id or frontmatter_id
        if canonical:
            doc_num_match = re.match(r"^PRD-(\d{2,9})$", canonical)
            if doc_num_match:
                doc_num = doc_num_match.group(1)
                element_ids = re.findall(r"\bPRD\.(\d{2,9})\.(\d{2})\.(\d{2,9})\b", content)
                mismatched = sorted({f"PRD.{n}.{tt}.{ss}" for n, tt, ss in element_ids if n != doc_num})
                if mismatched:
                    self.errors.append(
                        f"[{file_name}] PRD-E001: Element IDs must use document number '{doc_num}'. "
                        f"Found mismatches: {', '.join(mismatched[:5])}"
                    )

        # Enforce Layer-2 scope: forbid concrete downstream IDs (Layer 5+).
        forbidden = [
            r"\bADR-\d{2,9}\b",
            r"\bSYS-\d{2,9}\b",
            r"\bREQ-\d{2,9}\b",
            r"\bCTR-\d{2,9}\b",
            r"\bSPEC-\d{2,9}\b",
            r"\bTSPEC-\d{2,9}\b",
            r"\bTASKS-\d{2,9}\b",
        ]
        found = []
        for pattern in forbidden:
            found.extend(re.findall(pattern, content))
        if found:
            self.errors.append(
                f"[{file_name}] PRD-E022: PRD contains concrete downstream artifact IDs (Layer 5+): "
                f"{', '.join(sorted(set(found))[:5])}"
            )

        # Enforce traceability matrix presence and row membership.
        matrix_path = self._find_matrix_path(file_path)
        if matrix_path is None or not matrix_path.exists():
            self.errors.append(
                f"[{file_name}] PRD-E027: Missing required traceability matrix file PRD-00_TRACEABILITY_MATRIX.md"
            )
        else:
            doc_id = frontmatter_id or filename_id
            if doc_id:
                matrix_text = matrix_path.read_text(encoding="utf-8")
                if doc_id not in matrix_text:
                    self.warnings.append(
                        f"[{file_name}] PRD-W016: Traceability matrix missing entry for {doc_id}"
                    )

    def _extract_filename_doc_id(self, file_path: Path) -> str | None:
        match = re.match(r"^(PRD-\d{2,9})(?:\.\d+)?_", file_path.name)
        return match.group(1) if match else None

    def _extract_frontmatter_doc_id(self, content: str) -> str | None:
        match = re.search(r"(?im)^doc_id:\s*(PRD-\d{2,9})\s*$", content)
        return match.group(1) if match else None

    def _extract_h1_doc_id(self, content: str) -> str | None:
        match = re.search(r"^#\s+(PRD-\d{2,9}):", content, re.MULTILINE)
        return match.group(1) if match else None

    def _extract_doc_control_doc_id(self, content: str) -> str | None:
        match = re.search(r"(?im)^\s*-\s*Document\s+ID:\s*(PRD-\d{2,9})\s*$", content)
        return match.group(1) if match else None

    def _find_matrix_path(self, file_path: Path) -> Path | None:
        for path in [file_path.parent, *file_path.parents]:
            if path.name == "02_PRD":
                return path / "PRD-00_TRACEABILITY_MATRIX.md"
        return None

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
