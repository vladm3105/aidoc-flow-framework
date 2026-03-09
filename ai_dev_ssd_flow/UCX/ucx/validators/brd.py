"""BRD (Business Requirements Document) validator."""

from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.BRD)
class BRDValidator(BaseValidator):
    """Validator for Business Requirements Documents (Layer 1)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status"]

    REQUIRED_SECTIONS = [
        "Executive Summary",
        "Business Context",
        "Requirements",
        "Constraints",
    ]

    ELEMENT_ID_PATTERN = r"BRD\.\d+\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@ref:",
        r"@prd:",
    ]

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate a BRD file."""
        file_name = file_path.name

        # Check YAML frontmatter
        self.check_yaml_frontmatter(
            content,
            self.REQUIRED_FRONTMATTER,
            file_name,
        )

        # Check element IDs
        id_count = self.check_element_ids(
            content,
            self.ELEMENT_ID_PATTERN,
            file_name,
        )
        if id_count == 0:
            self.warnings.append(f"{file_name}: No BRD element IDs found")

        # Check required sections
        self.check_required_sections(
            content,
            self.REQUIRED_SECTIONS,
            file_name,
        )

        # Check traceability
        self.check_traceability(
            content,
            self.TRACE_PATTERNS,
            file_name,
        )

        # BRD-specific checks
        self._check_business_objectives(content, file_name)
        self._check_stakeholders(content, file_name)

    def _check_business_objectives(self, content: str, file_name: str) -> None:
        """Check for business objectives section."""
        if "business objective" in content.lower():
            self.passes.append(f"{file_name}: Contains business objectives")
        else:
            self.warnings.append(f"{file_name}: No business objectives found")

    def _check_stakeholders(self, content: str, file_name: str) -> None:
        """Check for stakeholder definitions."""
        if "stakeholder" in content.lower():
            self.passes.append(f"{file_name}: Contains stakeholder information")
        else:
            self.warnings.append(f"{file_name}: No stakeholder information found")
