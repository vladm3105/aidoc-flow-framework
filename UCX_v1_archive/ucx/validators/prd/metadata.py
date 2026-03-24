"""PRD Metadata Validation Module.

Validates:
- YAML frontmatter structure
- Required fields and tags
- Document Control section fields
- Status values
- Upstream traceability format
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from ucx.validators.prd import ValidationIssue, Tier
from ucx.validators.common.frontmatter import parse_frontmatter, FrontmatterResult
from ucx.validators.prd.schema import (
    REQUIRED_FRONTMATTER_FIELDS,
    REQUIRED_CUSTOM_FIELDS,
    REQUIRED_TAGS,
    DOC_CONTROL_REQUIRED_FIELDS,
    VALID_STATUS_VALUES,
    BRD_TRACE_PATTERN,
    BRD_TRACE_INVALID,
)


def validate_metadata(file_path: Path, content: str) -> List[ValidationIssue]:
    """Validate PRD metadata.

    Args:
        file_path: Path to PRD file
        content: File content

    Returns:
        List of validation issues
    """
    issues = []
    file_name = file_path.name

    # Parse frontmatter
    frontmatter_result = parse_frontmatter(content, file_name)

    if not frontmatter_result.is_valid:
        issues.append(ValidationIssue(
            code="CORPUS-W018",
            message="Missing or invalid YAML frontmatter",
            file=file_name,
            tier=Tier.TIER2,
        ))
        return issues

    # Get the frontmatter data dict
    frontmatter = frontmatter_result.data

    # Validate required frontmatter fields
    issues.extend(_validate_frontmatter_fields(file_name, frontmatter))

    # Validate tags
    issues.extend(_validate_tags(file_name, frontmatter))

    # Validate custom_fields
    issues.extend(_validate_custom_fields(file_name, frontmatter))

    # Validate Document Control section
    issues.extend(_validate_document_control(file_path, content))

    # Validate BRD traceability format
    issues.extend(_validate_brd_traceability(file_path, content))

    # Validate ID consistency across filename/frontmatter/H1/Document Control
    issues.extend(_validate_id_consistency(file_path, frontmatter, content))

    # Validate PRD traceability matrix presence and membership
    issues.extend(_validate_traceability_matrix(file_path, frontmatter))

    return issues


def _validate_frontmatter_fields(
    file_name: str,
    frontmatter: Dict[str, Any],
) -> List[ValidationIssue]:
    """Validate required frontmatter fields."""
    issues = []

    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in frontmatter:
            issues.append(ValidationIssue(
                code="CORPUS-W018",
                message=f"Missing required frontmatter field: {field}",
                file=file_name,
                tier=Tier.TIER2,
            ))

    # Validate doc_id format
    doc_id = frontmatter.get("doc_id", "")
    if doc_id and not re.match(r"^PRD-\d{2,9}$", str(doc_id)):
        issues.append(ValidationIssue(
            code="PRD-W002",
            message=f"Invalid doc_id format '{doc_id}', expected PRD-NN",
            file=file_name,
            tier=Tier.TIER2,
        ))

    # Validate status value
    status = frontmatter.get("status", "")
    if status and str(status).lower().capitalize() not in VALID_STATUS_VALUES:
        issues.append(ValidationIssue(
            code="PRD-W005",
            message=f"Invalid status '{status}', expected: {', '.join(VALID_STATUS_VALUES)}",
            file=file_name,
            tier=Tier.TIER2,
        ))

    return issues


def _validate_tags(
    file_name: str,
    frontmatter: Dict[str, Any],
) -> List[ValidationIssue]:
    """Validate required tags."""
    issues = []

    tags = frontmatter.get("tags", [])
    if not isinstance(tags, list):
        tags = [tags] if tags else []

    for required_tag in REQUIRED_TAGS:
        if required_tag not in tags:
            code = "PRD-E003" if required_tag == "prd" else "PRD-E004"
            issues.append(ValidationIssue(
                code=code,
                message=f"Missing required tag: {required_tag}",
                file=file_name,
                tier=Tier.TIER1,
            ))

    return issues


def _validate_custom_fields(
    file_name: str,
    frontmatter: Dict[str, Any],
) -> List[ValidationIssue]:
    """Validate custom_fields section."""
    issues = []

    custom_fields = frontmatter.get("custom_fields", {})
    if not isinstance(custom_fields, dict):
        custom_fields = {}

    for field, expected_value in REQUIRED_CUSTOM_FIELDS.items():
        actual_value = str(custom_fields.get(field, "")).lower()
        if actual_value != expected_value.lower():
            issues.append(ValidationIssue(
                code="PRD-E019",
                message=f"Missing or invalid custom_fields.{field} (expected: {expected_value})",
                file=file_name,
                tier=Tier.TIER1,
            ))

    return issues


def _validate_document_control(
    file_path: Path,
    content: str,
) -> List[ValidationIssue]:
    """Validate Document Control section."""
    issues = []
    file_name = file_path.name

    # Find Document Control section
    doc_control_match = re.search(
        r"(?:^## 0\.|^## 1\.|Document Control)(.*?)(?=^## \d+\.|\Z)",
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    if not doc_control_match:
        # Only require for main PRD files
        if _is_main_file(file_path):
            issues.append(ValidationIssue(
                code="PRD-E002",
                message="Missing Document Control section",
                file=file_name,
                tier=Tier.TIER1,
            ))
        return issues

    doc_control_content = doc_control_match.group(0)

    # Check for required fields in Document Control
    missing_fields = []
    for field in DOC_CONTROL_REQUIRED_FIELDS:
        # Skip revision history for Draft status
        if field == "Revision History":
            if "Draft" in doc_control_content:
                continue

        if field.lower() not in doc_control_content.lower():
            # Try alternate field names
            alternates = _get_field_alternates(field)
            if not any(alt.lower() in doc_control_content.lower() for alt in alternates):
                missing_fields.append(field)

    if missing_fields:
        issues.append(ValidationIssue(
            code="PRD-E019",
            message=f"Document Control missing fields: {', '.join(missing_fields)}",
            file=file_name,
            tier=Tier.TIER1,
        ))

    # Check date format
    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
    if not date_pattern.search(doc_control_content):
        # Check for non-ISO date format
        non_iso_date = re.search(r"\d{4}-\d{2}-\d{2}(?!T)", doc_control_content)
        if non_iso_date:
            issues.append(ValidationIssue(
                code="CORPUS-W019",
                message="Date format should be ISO 8601 (YYYY-MM-DDTHH:MM:SS)",
                file=file_name,
                tier=Tier.TIER2,
            ))

    return issues


def _validate_brd_traceability(
    file_path: Path,
    content: str,
) -> List[ValidationIssue]:
    """Validate BRD traceability format."""
    issues = []
    file_name = file_path.name

    # Check for valid BRD references (4-segment format)
    valid_refs = BRD_TRACE_PATTERN.findall(content)

    # Check for invalid BRD references (document-level only)
    invalid_refs = BRD_TRACE_INVALID.findall(content)

    if invalid_refs:
        for ref in invalid_refs[:3]:  # Limit to first 3
            issues.append(ValidationIssue(
                code="PRD-E018",
                message=f"Invalid BRD reference format '@brd: BRD-{ref}', use 4-segment: @brd: BRD.NN.TT.SS",
                file=file_name,
                tier=Tier.TIER1,
            ))

    # Check if any BRD traceability exists
    has_brd_ref = valid_refs or re.search(r"@brd:", content)
    if not has_brd_ref and _is_main_file(file_path):
        issues.append(ValidationIssue(
            code="CORPUS-E011",
            message="No @brd: traceability reference found",
            file=file_name,
            tier=Tier.TIER1,
        ))

    return issues


def _is_main_file(file_path: Path) -> bool:
    """Check if file is a main PRD file (not a section file)."""
    file_name = file_path.name
    # Section files have format PRD-NN.S_slug.md
    return not re.match(r"PRD-\d{2,9}\.\d+_", file_name)


def _extract_filename_doc_id(file_path: Path) -> Optional[str]:
    """Extract PRD-NN doc ID from filename."""
    match = re.match(r"^(PRD-\d{2,9})(?:\.\d+)?_", file_path.name)
    return match.group(1) if match else None


def _extract_h1_doc_id(content: str) -> Optional[str]:
    """Extract PRD-NN doc ID from H1 heading."""
    match = re.search(r"^#\s+(PRD-\d{2,9}):", content, re.MULTILINE)
    return match.group(1) if match else None


def _extract_doc_control_doc_id(content: str) -> Optional[str]:
    """Extract PRD-NN doc ID from Section 1 Document Control."""
    match = re.search(r"(?im)^\s*-\s*Document\s+ID:\s*(PRD-\d{2,9})\s*$", content)
    return match.group(1) if match else None


def _validate_id_consistency(
    file_path: Path,
    frontmatter: Dict[str, Any],
    content: str,
) -> List[ValidationIssue]:
    """Ensure filename/frontmatter/H1/Document Control use the same PRD-NN."""
    issues: List[ValidationIssue] = []
    file_name = file_path.name

    if not _is_main_file(file_path):
        return issues

    filename_id = _extract_filename_doc_id(file_path)
    frontmatter_id = str(frontmatter.get("doc_id", "")).strip() or None
    h1_id = _extract_h1_doc_id(content)
    doc_control_id = _extract_doc_control_doc_id(content)

    ids = {
        "filename": filename_id,
        "frontmatter": frontmatter_id,
        "h1": h1_id,
        "document_control": doc_control_id,
    }

    present_ids = {v for v in ids.values() if v}
    if len(present_ids) > 1:
        issues.append(ValidationIssue(
            code="PRD-E001",
            message=(
                "Inconsistent PRD document ID across filename/frontmatter/H1/Document Control: "
                f"{ids}"
            ),
            file=file_name,
            tier=Tier.TIER1,
        ))

    canonical_id = filename_id or frontmatter_id
    if canonical_id:
        doc_num_match = re.match(r"PRD-(\d{2,9})$", canonical_id)
        if doc_num_match:
            doc_num = doc_num_match.group(1)
            element_ids = re.findall(r"\bPRD\.(\d{2,9})\.(\d{2})\.(\d{2,9})\b", content)
            mismatched = sorted({f"PRD.{n}.{tt}.{ss}" for n, tt, ss in element_ids if n != doc_num})
            if mismatched:
                issues.append(ValidationIssue(
                    code="PRD-E001",
                    message=(
                        f"Element IDs must use document number '{doc_num}' from {canonical_id}. "
                        f"Found mismatches: {', '.join(mismatched[:5])}"
                    ),
                    file=file_name,
                    tier=Tier.TIER1,
                ))

    return issues


def _find_prd_root_dir(file_path: Path) -> Optional[Path]:
    """Find the nearest 02_PRD directory for the current file."""
    search_paths = [file_path.parent, *file_path.parents]
    for path in search_paths:
        if path.name == "02_PRD":
            return path
    return None


def _validate_traceability_matrix(
    file_path: Path,
    frontmatter: Dict[str, Any],
) -> List[ValidationIssue]:
    """Validate PRD traceability matrix presence and PRD entry."""
    issues: List[ValidationIssue] = []
    file_name = file_path.name

    if not _is_main_file(file_path):
        return issues

    prd_root = _find_prd_root_dir(file_path)
    if prd_root is None:
        return issues

    matrix_path = prd_root / "PRD-00_TRACEABILITY_MATRIX.md"
    if not matrix_path.exists():
        issues.append(ValidationIssue(
            code="PRD-E027",
            message=(
                "Missing required traceability matrix file 'PRD-00_TRACEABILITY_MATRIX.md' "
                "in 02_PRD directory"
            ),
            file=file_name,
            tier=Tier.TIER1,
        ))
        return issues

    doc_id = str(frontmatter.get("doc_id", "")).strip() or _extract_filename_doc_id(file_path)
    if not doc_id:
        return issues

    matrix_text = matrix_path.read_text(encoding="utf-8")
    if doc_id not in matrix_text:
        issues.append(ValidationIssue(
            code="PRD-W016",
            message=(
                f"Traceability matrix missing entry for {doc_id}. "
                "Update PRD-00_TRACEABILITY_MATRIX.md in the same change set"
            ),
            file=file_name,
            tier=Tier.TIER2,
        ))

    return issues


def _get_field_alternates(field: str) -> List[str]:
    """Get alternate names for a field."""
    alternates_map = {
        "Date Created": ["Created", "Creation Date", "Created Date"],
        "Last Updated": ["Updated", "Last Modified", "Modified Date"],
        "BRD Reference": ["BRD", "@brd", "Upstream"],
        "SYS-Ready Score": ["SYS-Ready", "SYS Ready", "System Ready"],
        "EARS-Ready Score": ["EARS-Ready", "EARS Ready"],
        "Revision History": ["History", "Changes", "Revisions"],
    }
    return alternates_map.get(field, [field])


def extract_frontmatter_values(content: str) -> Dict[str, Any]:
    """Extract key values from frontmatter for use by other modules."""
    frontmatter_result = parse_frontmatter(content)
    if not frontmatter_result.is_valid:
        return {}

    frontmatter = frontmatter_result.data
    custom_fields = frontmatter.get("custom_fields", {})
    if not isinstance(custom_fields, dict):
        custom_fields = {}

    return {
        "doc_id": frontmatter.get("doc_id", ""),
        "version": frontmatter.get("version", ""),
        "status": frontmatter.get("status", ""),
        "tags": frontmatter.get("tags", []),
        "custom_fields": custom_fields,
        "upstream": custom_fields.get("upstream_artifacts", []),
        "downstream": custom_fields.get("downstream_artifacts", []),
    }
