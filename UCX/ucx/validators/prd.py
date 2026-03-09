"""PRD (Product Requirements Document) validator."""

from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.PRD)
class PRDValidator(BaseValidator):
    """Validator for Product Requirements Documents (Layer 2)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status"]

    REQUIRED_SECTIONS = [
        "Product Overview",
        "User Stories",
        "Acceptance Criteria",
        "Dependencies",
    ]

    ELEMENT_ID_PATTERN = r"PRD\.\d+\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@brd:",
        r"@ears:",
    ]

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate a PRD file."""
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
            self.warnings.append(f"{file_name}: No PRD element IDs found")

        # Check required sections
        self.check_required_sections(
            content,
            self.REQUIRED_SECTIONS,
            file_name,
        )

        # Check traceability to BRD
        self.check_traceability(
            content,
            self.TRACE_PATTERNS,
            file_name,
        )

        # PRD-specific checks
        self._check_user_personas(content, file_name)
        self._check_feature_priority(content, file_name)

    def _check_user_personas(self, content: str, file_name: str) -> None:
        """Check for user persona definitions."""
        if "persona" in content.lower() or "user type" in content.lower():
            self.passes.append(f"{file_name}: Contains user personas")
        else:
            self.warnings.append(f"{file_name}: No user personas found")

    def _check_feature_priority(self, content: str, file_name: str) -> None:
        """Check for feature priority indicators."""
        priority_terms = ["must have", "should have", "could have", "p0", "p1", "p2", "priority"]
        if any(term in content.lower() for term in priority_terms):
            self.passes.append(f"{file_name}: Contains priority indicators")
        else:
            self.warnings.append(f"{file_name}: No priority indicators found")
