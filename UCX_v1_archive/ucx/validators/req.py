"""REQ (Atomic Requirements) validator."""

import re
from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.REQ)
class REQValidator(BaseValidator):
    """Validator for Atomic Requirements Documents (Layer 7)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status", "parent_sys"]

    REQUIRED_SECTIONS = [
        "Requirement",
        "Acceptance Criteria",
    ]

    OPTIONAL_SECTIONS = [
        "Rationale",
        "Dependencies",
        "Test Approach",
    ]

    ELEMENT_ID_PATTERN = r"REQ\.\d+\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@sys:",
        r"@ctr:",
        r"@spec:",
    ]

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate a REQ file."""
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
            self.warnings.append(f"{file_name}: No REQ element IDs found")

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

        # REQ-specific checks
        self._check_atomic_structure(content, file_name)
        self._check_acceptance_criteria(content, file_name)
        self._check_testability(content, file_name)
        self._check_parent_traceability(content, file_name)

    def _check_atomic_structure(self, content: str, file_name: str) -> None:
        """Check that requirements are atomic (single responsibility)."""
        # Count requirements
        req_ids = re.findall(self.ELEMENT_ID_PATTERN, content)

        # Check for compound requirements (and/or in the same requirement)
        compound_indicators = re.findall(
            r"(shall\s+\w+\s+and\s+shall|shall\s+both|shall\s+either)",
            content,
            re.IGNORECASE
        )

        if compound_indicators:
            self.warnings.append(
                f"{file_name}: Possible compound requirements detected - consider splitting"
            )
        elif req_ids:
            self.passes.append(f"{file_name}: Requirements appear atomic")

    def _check_acceptance_criteria(self, content: str, file_name: str) -> None:
        """Check acceptance criteria format."""
        # Look for acceptance criteria patterns
        ac_patterns = [
            r"^\s*[-*]\s*(Given|When|Then)",  # Gherkin-style
            r"^\s*[-*]\s*AC[-.]?\d+",  # AC-1, AC.1 style
            r"acceptance\s+criteria\s*:?\s*\n\s*[-*]",  # List under header
        ]

        found = False
        for pattern in ac_patterns:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                found = True
                break

        if found:
            self.passes.append(f"{file_name}: Acceptance criteria present")
        else:
            self.warnings.append(
                f"{file_name}: No structured acceptance criteria found"
            )

    def _check_testability(self, content: str, file_name: str) -> None:
        """Check for testability indicators."""
        testability_keywords = [
            r"\btest(able|ability)\b",
            r"\bverif(y|ication|iable)\b",
            r"\bmeasur(e|able|ement)\b",
            r"\bvalidat(e|ion)\b",
        ]

        found = []
        for pattern in testability_keywords:
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pattern.replace(r"\b", "").split("(")[0])

        if found:
            self.passes.append(f"{file_name}: Testability considered")
        else:
            self.warnings.append(
                f"{file_name}: Consider adding testability information"
            )

    def _check_parent_traceability(self, content: str, file_name: str) -> None:
        """Check for parent system requirement traceability."""
        # Check frontmatter for parent_sys
        parent_match = re.search(r"parent_sys:\s*(SYS[-._]\d+)", content, re.IGNORECASE)

        if parent_match:
            self.passes.append(
                f"{file_name}: Traces to parent: {parent_match.group(1)}"
            )
        else:
            # Check for @sys: tags
            sys_refs = re.findall(r"@sys:\s*(SYS[-._]\d+)", content, re.IGNORECASE)
            if sys_refs:
                self.passes.append(
                    f"{file_name}: References SYS requirements"
                )
            else:
                self.warnings.append(
                    f"{file_name}: No parent SYS requirement traced"
                )
