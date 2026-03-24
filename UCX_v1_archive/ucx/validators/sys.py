"""SYS (System Requirements) validator."""

import re
from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.SYS)
class SYSValidator(BaseValidator):
    """Validator for System Requirements Documents (Layer 6)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status"]

    REQUIRED_SECTIONS = [
        "Functional Requirements",
        "Non-Functional Requirements",
        "System Interfaces",
    ]

    OPTIONAL_SECTIONS = [
        "Performance Requirements",
        "Security Requirements",
        "Scalability Requirements",
        "System Constraints",
    ]

    ELEMENT_ID_PATTERN = r"SYS\.\d+\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@adr:",
        r"@req:",
        r"@brd:",
    ]

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate a SYS file."""
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
            self.warnings.append(f"{file_name}: No SYS element IDs found")

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

        # SYS-specific checks
        self._check_functional_requirements(content, file_name)
        self._check_nonfunctional_requirements(content, file_name)
        self._check_interface_definitions(content, file_name)
        self._check_requirements_format(content, file_name)

    def _check_functional_requirements(self, content: str, file_name: str) -> None:
        """Check for functional requirements."""
        # Look for FR identifiers or functional requirement section content
        fr_patterns = [
            r"FR[-.]?\d+",
            r"SYS\.FR\.\d+",
            r"functional\s+requirement",
        ]

        found = False
        for pattern in fr_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found = True
                break

        if found:
            self.passes.append(f"{file_name}: Contains functional requirements")
        else:
            self.warnings.append(f"{file_name}: No functional requirements identified")

    def _check_nonfunctional_requirements(self, content: str, file_name: str) -> None:
        """Check for non-functional requirements categories."""
        nfr_categories = [
            "performance",
            "security",
            "scalability",
            "reliability",
            "availability",
            "maintainability",
            "usability",
        ]

        found_categories = []
        for category in nfr_categories:
            if re.search(rf"\b{category}\b", content, re.IGNORECASE):
                found_categories.append(category)

        if len(found_categories) >= 3:
            self.passes.append(
                f"{file_name}: Comprehensive NFRs ({', '.join(found_categories)})"
            )
        elif len(found_categories) >= 1:
            self.passes.append(
                f"{file_name}: Contains NFRs: {', '.join(found_categories)}"
            )
        else:
            self.warnings.append(f"{file_name}: No NFR categories identified")

    def _check_interface_definitions(self, content: str, file_name: str) -> None:
        """Check for interface definitions."""
        interface_indicators = [
            r"\bAPI\b",
            r"\bREST\b",
            r"\bGraphQL\b",
            r"\bgRPC\b",
            r"\binterface\b",
            r"\bendpoint\b",
            r"\bcontract\b",
        ]

        found = []
        for pattern in interface_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pattern.replace(r"\b", "").strip())

        if found:
            self.passes.append(f"{file_name}: Interface definitions present")
        else:
            self.warnings.append(f"{file_name}: No interface definitions found")

    def _check_requirements_format(self, content: str, file_name: str) -> None:
        """Check requirements use standard format."""
        # Check for SHALL/MUST/SHOULD patterns
        shall_count = len(re.findall(r"\b(shall|must)\b", content, re.IGNORECASE))
        should_count = len(re.findall(r"\bshould\b", content, re.IGNORECASE))

        if shall_count > 0:
            self.passes.append(
                f"{file_name}: Uses formal requirements language (shall/must: {shall_count})"
            )
        else:
            self.warnings.append(
                f"{file_name}: Consider using formal requirements language (shall/must)"
            )
