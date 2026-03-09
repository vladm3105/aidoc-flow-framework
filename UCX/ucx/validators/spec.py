"""SPEC (Technical Specification) validator."""

import re
from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.SPEC)
class SPECValidator(BaseValidator):
    """Validator for Technical Specification Documents (Layer 9)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status"]

    REQUIRED_SECTIONS = [
        "Implementation",
        "Data Model",
        "Error Handling",
    ]

    OPTIONAL_SECTIONS = [
        "Architecture",
        "Dependencies",
        "Configuration",
        "Performance",
        "Security",
        "Testing",
    ]

    ELEMENT_ID_PATTERN = r"SPEC\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@req:",
        r"@ctr:",
        r"@tspec:",
    ]

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate a SPEC file."""
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
            self.warnings.append(f"{file_name}: No SPEC element IDs found")

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

        # SPEC-specific checks
        self._check_implementation_details(content, file_name)
        self._check_data_model(content, file_name)
        self._check_error_handling(content, file_name)
        self._check_code_examples(content, file_name)

    def _check_implementation_details(self, content: str, file_name: str) -> None:
        """Check for implementation details."""
        impl_indicators = [
            r"\bfunction\b|\bmethod\b|\bclass\b",
            r"\balgorithm\b",
            r"\bimplementation\b",
            r"\bpseudocode\b",
            r"```(python|typescript|java|go|rust)",
        ]

        found = []
        for pattern in impl_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pattern)

        if found:
            self.passes.append(f"{file_name}: Implementation details present")
        else:
            self.warnings.append(
                f"{file_name}: Limited implementation details"
            )

    def _check_data_model(self, content: str, file_name: str) -> None:
        """Check for data model definitions."""
        model_indicators = [
            r"\bschema\b",
            r"\bmodel\b",
            r"\bentity\b",
            r"\bfield(s)?\b",
            r"\btype(s)?\s*:",
            r"\bproperties\b",
            r"\bclass\s+\w+",
            r"\binterface\s+\w+",
        ]

        found = []
        for pattern in model_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pattern)

        if len(found) >= 2:
            self.passes.append(f"{file_name}: Data model well-defined")
        elif len(found) == 1:
            self.passes.append(f"{file_name}: Data model present")
        else:
            self.warnings.append(f"{file_name}: No data model defined")

    def _check_error_handling(self, content: str, file_name: str) -> None:
        """Check for error handling specifications."""
        error_indicators = [
            r"\berror\b",
            r"\bexception\b",
            r"\bfailure\b",
            r"\bfallback\b",
            r"\bretry\b",
            r"\btimeout\b",
            r"\brecovery\b",
            r"\brollback\b",
        ]

        found = []
        for pattern in error_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                keyword = pattern.replace(r"\b", "")
                found.append(keyword)

        if len(found) >= 3:
            self.passes.append(
                f"{file_name}: Comprehensive error handling ({', '.join(found[:3])}...)"
            )
        elif found:
            self.passes.append(f"{file_name}: Error handling addressed")
        else:
            self.warnings.append(f"{file_name}: No error handling specified")

    def _check_code_examples(self, content: str, file_name: str) -> None:
        """Check for code examples."""
        code_blocks = re.findall(r"```\w+", content)

        if len(code_blocks) >= 2:
            self.passes.append(
                f"{file_name}: Multiple code examples ({len(code_blocks)} blocks)"
            )
        elif len(code_blocks) == 1:
            self.passes.append(f"{file_name}: Code example present")
        else:
            self.warnings.append(
                f"{file_name}: No code examples found - consider adding"
            )
