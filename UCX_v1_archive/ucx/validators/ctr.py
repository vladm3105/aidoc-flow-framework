"""CTR (Data Contracts) validator."""

import re
from pathlib import Path

from ucx.models.enums import DocType
from ucx.validators.base import BaseValidator
from ucx.validators.registry import register_validator


@register_validator(DocType.CTR)
class CTRValidator(BaseValidator):
    """Validator for Data Contract Documents (Layer 8)."""

    REQUIRED_FRONTMATTER = ["title", "doc_id", "version", "status", "contract_type"]

    REQUIRED_SECTIONS = [
        "Schema",
        "Validation Rules",
    ]

    OPTIONAL_SECTIONS = [
        "Examples",
        "Error Handling",
        "Versioning",
        "Dependencies",
    ]

    ELEMENT_ID_PATTERN = r"CTR\.\d+\.\d+"

    TRACE_PATTERNS = [
        r"@req:",
        r"@spec:",
        r"@api:",
    ]

    # Valid contract types
    VALID_CONTRACT_TYPES = [
        "api",
        "event",
        "message",
        "data",
        "interface",
    ]

    def _validate_file(self, file_path: Path, content: str) -> None:
        """Validate a CTR file."""
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
            self.warnings.append(f"{file_name}: No CTR element IDs found")

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

        # CTR-specific checks
        self._check_contract_type(content, file_name)
        self._check_schema_definition(content, file_name)
        self._check_validation_rules(content, file_name)
        self._check_examples(content, file_name)

    def _check_contract_type(self, content: str, file_name: str) -> None:
        """Check for valid contract type."""
        match = re.search(r"contract_type:\s*(\w+)", content, re.IGNORECASE)
        if match:
            contract_type = match.group(1).lower()
            if contract_type in self.VALID_CONTRACT_TYPES:
                self.passes.append(f"{file_name}: Valid contract type: {contract_type}")
            else:
                self.warnings.append(
                    f"{file_name}: Unusual contract type: {contract_type}. "
                    f"Common types: {', '.join(self.VALID_CONTRACT_TYPES)}"
                )

    def _check_schema_definition(self, content: str, file_name: str) -> None:
        """Check for schema definition."""
        schema_indicators = [
            r"```(json|yaml|typescript|python)",  # Code blocks
            r"\btype:\s*(string|integer|boolean|object|array)",  # Type definitions
            r"\bproperties:\s*\n",  # JSON Schema
            r"\bschema:\s*\n",  # Schema section
            r"interface\s+\w+\s*\{",  # TypeScript interface
            r"class\s+\w+.*:",  # Python class
            r"\$ref:\s*",  # JSON Schema reference
        ]

        found = []
        for pattern in schema_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pattern)

        if len(found) >= 2:
            self.passes.append(f"{file_name}: Well-defined schema present")
        elif len(found) == 1:
            self.passes.append(f"{file_name}: Schema definition found")
        else:
            self.errors.append(f"{file_name}: No schema definition found")

    def _check_validation_rules(self, content: str, file_name: str) -> None:
        """Check for validation rules."""
        validation_patterns = [
            r"\brequired\b",
            r"\boptional\b",
            r"\bminimum\b|\bmaximum\b",
            r"\bminLength\b|\bmaxLength\b",
            r"\bpattern\b",
            r"\benum\b",
            r"\bformat\b",
            r"must\s+be\s+",
            r"valid(ation|ate)",
        ]

        found = []
        for pattern in validation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pattern.split(r"\b")[1] if r"\b" in pattern else pattern)

        if found:
            self.passes.append(
                f"{file_name}: Validation rules defined ({len(found)} types)"
            )
        else:
            self.warnings.append(f"{file_name}: No explicit validation rules found")

    def _check_examples(self, content: str, file_name: str) -> None:
        """Check for contract examples."""
        # Look for example section or code blocks following example text
        has_example_section = bool(
            re.search(r"#+\s*example", content, re.IGNORECASE)
        )
        has_example_blocks = bool(
            re.search(r"example.*?```", content, re.IGNORECASE | re.DOTALL)
        )

        if has_example_section or has_example_blocks:
            self.passes.append(f"{file_name}: Contains examples")
        else:
            self.warnings.append(f"{file_name}: No examples provided")
