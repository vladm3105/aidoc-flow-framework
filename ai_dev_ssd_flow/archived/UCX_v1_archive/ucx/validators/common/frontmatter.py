"""YAML frontmatter parsing utilities for UCX validators.

Provides:
- Frontmatter extraction and parsing
- Field validation with type checking
- Custom field validation
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml

from ucx.validators.common.patterns import YAML_FRONTMATTER_PATTERN


@dataclass
class FrontmatterResult:
    """Result of frontmatter parsing."""

    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    raw_yaml: str = ""

    @property
    def is_valid(self) -> bool:
        """Check if parsing succeeded without errors."""
        return len(self.errors) == 0

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from frontmatter."""
        return self.data.get(key, default)

    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """Get a nested value from frontmatter."""
        current = self.data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
                if current is None:
                    return default
            else:
                return default
        return current


def parse_frontmatter(content: str, file_name: str = "") -> FrontmatterResult:
    """
    Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown file content
        file_name: File name for error messages

    Returns:
        FrontmatterResult with parsed data and any errors
    """
    result = FrontmatterResult()
    prefix = f"{file_name}: " if file_name else ""

    # Check for frontmatter presence
    if not content.startswith("---"):
        result.errors.append(f"{prefix}Missing YAML frontmatter")
        return result

    # Extract frontmatter block
    match = YAML_FRONTMATTER_PATTERN.match(content)
    if not match:
        result.errors.append(f"{prefix}Malformed YAML frontmatter (missing closing ---)")
        return result

    result.raw_yaml = match.group(1)

    # Parse YAML
    try:
        parsed = yaml.safe_load(result.raw_yaml)
        if parsed is None:
            result.data = {}
        elif isinstance(parsed, dict):
            result.data = parsed
        else:
            result.errors.append(f"{prefix}Frontmatter must be a YAML mapping")
    except yaml.YAMLError as e:
        result.errors.append(f"{prefix}Invalid YAML: {e}")

    return result


def validate_frontmatter_fields(
    result: FrontmatterResult,
    required_fields: List[str],
    file_name: str = "",
) -> bool:
    """
    Validate that required fields are present in frontmatter.

    Args:
        result: Parsed frontmatter result
        required_fields: List of required field names
        file_name: File name for error messages

    Returns:
        True if all required fields present
    """
    prefix = f"{file_name}: " if file_name else ""
    valid = True

    for field_name in required_fields:
        if field_name not in result.data:
            result.errors.append(f"{prefix}Missing required field: {field_name}")
            valid = False

    return valid


def validate_custom_fields(
    result: FrontmatterResult,
    field_specs: Dict[str, Dict[str, Any]],
    file_name: str = "",
) -> bool:
    """
    Validate custom_fields against specifications.

    Args:
        result: Parsed frontmatter result
        field_specs: Dict mapping field names to their specs:
            - allowed: List of allowed values
            - type: Expected type ('array', 'string', 'int')
            - required: Whether field is required (default True)
        file_name: File name for error messages

    Returns:
        True if all custom fields are valid
    """
    prefix = f"{file_name}: " if file_name else ""
    custom_fields = result.data.get("custom_fields", {})

    if not isinstance(custom_fields, dict):
        result.errors.append(f"{prefix}custom_fields must be a mapping")
        return False

    valid = True

    for field_name, spec in field_specs.items():
        is_required = spec.get("required", True)

        if field_name not in custom_fields:
            if is_required:
                result.errors.append(
                    f"{prefix}Missing required custom_field: {field_name}"
                )
                valid = False
            continue

        value = custom_fields[field_name]

        # Check allowed values
        if "allowed" in spec:
            if value not in spec["allowed"]:
                result.errors.append(
                    f"{prefix}Invalid value for {field_name}: {value} "
                    f"(allowed: {spec['allowed']})"
                )
                valid = False

        # Check type
        if "type" in spec:
            expected_type = spec["type"]
            if expected_type == "array" and not isinstance(value, list):
                result.errors.append(
                    f"{prefix}{field_name} must be an array, got {type(value).__name__}"
                )
                valid = False
            elif expected_type == "string" and not isinstance(value, str):
                result.errors.append(
                    f"{prefix}{field_name} must be a string, got {type(value).__name__}"
                )
                valid = False
            elif expected_type == "int" and not isinstance(value, int):
                result.errors.append(
                    f"{prefix}{field_name} must be an integer, got {type(value).__name__}"
                )
                valid = False

    return valid


def validate_tags(
    result: FrontmatterResult,
    required_tags: Set[str],
    forbidden_patterns: Optional[List[re.Pattern]] = None,
    file_name: str = "",
) -> bool:
    """
    Validate tags in frontmatter.

    Args:
        result: Parsed frontmatter result
        required_tags: Set of required tag values
        forbidden_patterns: List of regex patterns for forbidden tags
        file_name: File name for error messages

    Returns:
        True if all tag requirements met
    """
    prefix = f"{file_name}: " if file_name else ""
    tags = result.data.get("tags", [])

    if not isinstance(tags, list):
        result.errors.append(f"{prefix}tags must be an array")
        return False

    tags_set = set(tags)
    valid = True

    # Check required tags
    for required in required_tags:
        if required not in tags_set:
            result.errors.append(f"{prefix}Missing required tag: {required}")
            valid = False

    # Check forbidden patterns
    if forbidden_patterns:
        for tag in tags:
            for pattern in forbidden_patterns:
                if pattern.match(tag):
                    result.warnings.append(
                        f"{prefix}Tag matches forbidden pattern: {tag}"
                    )

    return valid


def check_legacy_status(
    result: FrontmatterResult,
    legacy_values: Set[str],
    file_name: str = "",
) -> None:
    """
    Check for legacy status values and add migration warning.

    Args:
        result: Parsed frontmatter result
        legacy_values: Set of legacy status values
        file_name: File name for messages
    """
    prefix = f"{file_name}: " if file_name else ""
    custom_fields = result.data.get("custom_fields", {})

    # Check for old development_status field
    if "development_status" in custom_fields:
        result.warnings.append(
            f"{prefix}Deprecated field 'development_status' found. "
            "Use 'status' instead."
        )

    # Check status value
    status = custom_fields.get("status")
    if status in legacy_values:
        result.warnings.append(
            f"{prefix}Legacy status value '{status}'. "
            "Consider updating to 'development' or 'production'."
        )
