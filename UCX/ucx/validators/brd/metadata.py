"""BRD metadata validation.

Validates:
- YAML frontmatter presence and format
- Required custom_fields
- Required tags
- Forbidden tag patterns
- Legacy field detection and migration warnings
"""

import re
from pathlib import Path
from typing import Set

from ucx.validators.common.result import (
    UnifiedValidationResult,
    ValidationTier,
)
from ucx.validators.common.frontmatter import (
    FrontmatterResult,
    validate_custom_fields,
    validate_tags,
    check_legacy_status,
)
from ucx.validators.brd.schema import (
    REQUIRED_CUSTOM_FIELDS,
    REQUIRED_TAGS,
    FORBIDDEN_TAG_PATTERNS,
    LEGACY_STATUS_VALUES,
)


def validate_metadata(
    content: str,
    frontmatter: FrontmatterResult,
    file_path: Path,
    result: UnifiedValidationResult,
    is_template: bool = False,
) -> None:
    """
    Validate BRD metadata.

    Args:
        content: File content
        frontmatter: Parsed frontmatter
        file_path: Path to file
        result: Result to populate
        is_template: Whether file is a template
    """
    # Validate custom_fields
    _validate_custom_fields(frontmatter, file_path, result)

    # Validate tags (skip for templates)
    if not is_template:
        _validate_tags(frontmatter, file_path, result)

    # Check for legacy status values
    _check_legacy_status(frontmatter, file_path, result)

    # Check for @depends tags on platform BRDs
    _check_depends_tags(content, file_path, result)


def _validate_custom_fields(
    frontmatter: FrontmatterResult,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """Validate required custom_fields."""
    custom_fields = frontmatter.data.get("custom_fields", {})

    if not custom_fields:
        result.add_issue(
            "BRD-E002",
            file_path=file_path,
            context="Missing custom_fields in frontmatter",
            tier=ValidationTier.TIER1,
        )
        return

    if not isinstance(custom_fields, dict):
        result.add_issue(
            "BRD-E002",
            file_path=file_path,
            context="custom_fields must be a mapping",
            tier=ValidationTier.TIER1,
        )
        return

    # Handle legacy development_status -> status migration
    status = custom_fields.get("status")
    legacy_status = custom_fields.get("development_status")

    if status is None and legacy_status is not None:
        if legacy_status in LEGACY_STATUS_VALUES:
            result.add_issue(
                "BRD-W005",
                file_path=file_path,
                context="Legacy development_status detected; migrate to status",
                tier=ValidationTier.TIER2,
            )
            # Use legacy value for validation
            custom_fields["status"] = legacy_status
        else:
            result.add_issue(
                "BRD-E002",
                file_path=file_path,
                context=f"Invalid legacy development_status: '{legacy_status}'",
                tier=ValidationTier.TIER1,
            )
    elif legacy_status is not None and status is not None:
        result.add_issue(
            "BRD-W005",
            file_path=file_path,
            context="Both status and legacy development_status present; status is authoritative",
            tier=ValidationTier.TIER2,
        )

    # Validate each required field
    for field_name, rules in REQUIRED_CUSTOM_FIELDS.items():
        value = custom_fields.get(field_name)

        if value is None:
            result.add_issue(
                "BRD-E002",
                file_path=file_path,
                context=f"Missing required field: custom_fields.{field_name}",
                tier=ValidationTier.TIER1,
            )
            continue

        # Check allowed values
        if "allowed" in rules:
            if value not in rules["allowed"]:
                result.add_issue(
                    "BRD-E002",
                    file_path=file_path,
                    context=f"Invalid value for {field_name}: '{value}'. Allowed: {rules['allowed']}",
                    tier=ValidationTier.TIER1,
                )

        # Check type
        if "type" in rules:
            if rules["type"] == "array" and not isinstance(value, list):
                result.add_issue(
                    "BRD-E002",
                    file_path=file_path,
                    context=f"Field {field_name} must be an array, got {type(value).__name__}",
                    tier=ValidationTier.TIER1,
                )

    result.add_pass(f"{file_path.name}: Custom fields validated")


def _validate_tags(
    frontmatter: FrontmatterResult,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """Validate required and forbidden tags."""
    tags = frontmatter.data.get("tags", [])

    if not isinstance(tags, list):
        result.add_issue(
            "BRD-E003",
            file_path=file_path,
            context="Tags must be an array",
            tier=ValidationTier.TIER1,
        )
        return

    tags_set = set(tags)

    # Check required tags
    for required_tag in REQUIRED_TAGS:
        if required_tag not in tags_set:
            if required_tag == "brd":
                result.add_issue(
                    "BRD-E003",
                    file_path=file_path,
                    context=f"Missing required tag: '{required_tag}'",
                    tier=ValidationTier.TIER1,
                )
            elif required_tag == "layer-1-artifact":
                result.add_issue(
                    "BRD-E004",
                    file_path=file_path,
                    context=f"Missing required tag: '{required_tag}'",
                    tier=ValidationTier.TIER1,
                )

    # Check for forbidden tags
    for tag in tags:
        for pattern in FORBIDDEN_TAG_PATTERNS:
            if pattern.match(str(tag)):
                result.add_issue(
                    "BRD-E003",
                    file_path=file_path,
                    context=f"Forbidden tag pattern: '{tag}'",
                    tier=ValidationTier.TIER1,
                )

    result.add_pass(f"{file_path.name}: Tags validated")


def _check_legacy_status(
    frontmatter: FrontmatterResult,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """Check for legacy status values that should be migrated."""
    custom_fields = frontmatter.data.get("custom_fields", {})
    status = custom_fields.get("status")

    if status in LEGACY_STATUS_VALUES:
        result.add_issue(
            "VAL-W002",
            file_path=file_path,
            context=f"Legacy status '{status}'. Consider updating to 'development' or 'production'",
            tier=ValidationTier.TIER2,
        )


def _check_depends_tags(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """Check for @depends tags on platform BRDs."""
    # Extract BRD number from file name
    match = re.search(r"BRD-(\d{2,})", file_path.name)
    if not match:
        return

    brd_num = int(match.group(1))

    # Platform BRDs (02-35) should have @depends tags
    if 2 <= brd_num <= 35:
        depends_count = content.count("@depends:")
        if depends_count == 0:
            result.add_issue(
                "BRD-W010",
                file_path=file_path,
                context="Platform BRD should have @depends tags for upstream BRD dependencies",
                tier=ValidationTier.TIER2,
            )
