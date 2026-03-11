"""BRD document structure validation.

Validates:
- File naming conventions
- H1 title format
- Required sections by profile (standard/MVP)
- Section numbering sequence
- Document Control section
- Business requirements structure
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from ucx.validators.common.result import (
    UnifiedValidationResult,
    ValidationTier,
)
from ucx.validators.brd.schema import (
    FILE_NAME_PATTERN_MONOLITHIC,
    FILE_NAME_PATTERN_SECTION_SHORT,
    FILE_NAME_PATTERN_SECTION_FULL,
    H1_TITLE_PATTERN,
    SECTION_NUMBER_PATTERN,
    SECTION_PROFILES,
    DOCUMENT_CONTROL_FIELDS,
)


def extract_sections(content: str) -> List[Tuple[str, int]]:
    """
    Extract section headers and their line numbers.

    Args:
        content: File content

    Returns:
        List of (header text, line number)
    """
    sections = []
    lines = content.split("\n")
    in_code_block = False

    for i, line in enumerate(lines, 1):
        # Toggle code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip content inside code blocks
        if in_code_block:
            continue

        if line.startswith("#"):
            sections.append((line, i))

    return sections


def validate_structure(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
    profile: str = "standard",
    is_section_layout: bool = False,
) -> None:
    """
    Validate BRD document structure.

    Args:
        content: File content
        file_path: Path to file
        result: Result to populate
        profile: Template profile (standard/mvp)
        is_section_layout: True if document uses section-based layout (multiple files)
    """
    # Validate file name
    _validate_file_name(file_path, result)

    # Extract sections
    sections = extract_sections(content)

    # Validate H1 title (for index files in section layout, allow "Section N:" format)
    _validate_h1_title(sections, file_path, result, is_section_layout)

    # For section-based layouts, skip required section validation
    # Sections are distributed across multiple files, not all in one document
    if not is_section_layout:
        # Validate required sections (monolithic only)
        _validate_required_sections(sections, file_path, result, profile)

        # Validate section numbering (monolithic only)
        _validate_section_numbering(sections, file_path, result)

        # Validate business requirements structure (monolithic only)
        _validate_business_requirements(content, file_path, result, profile)

    # Validate Document Control (both layouts, but with relaxed pattern for section layout)
    _validate_document_control(content, file_path, result, is_section_layout)


def _validate_file_name(
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """Validate file naming convention."""
    file_name = file_path.name

    # Skip template files
    if "TEMPLATE" in file_name.upper():
        return

    # Check against all valid patterns
    is_monolithic = FILE_NAME_PATTERN_MONOLITHIC.match(file_name)
    is_section_short = FILE_NAME_PATTERN_SECTION_SHORT.match(file_name)
    is_section_full = FILE_NAME_PATTERN_SECTION_FULL.match(file_name)

    if not (is_monolithic or is_section_short or is_section_full):
        result.add_issue(
            "BRD-W006",
            file_path=file_path,
            context=f"File name '{file_name}' doesn't match BRD format",
            tier=ValidationTier.TIER2,
        )


def _validate_h1_title(
    sections: List[Tuple[str, int]],
    file_path: Path,
    result: UnifiedValidationResult,
    is_section_layout: bool = False,
) -> None:
    """Validate H1 title format."""
    h1_sections = [s for s in sections if s[0].startswith("# ") and not s[0].startswith("## ")]

    if len(h1_sections) == 0:
        result.add_issue(
            "BRD-E001",
            file_path=file_path,
            context="Missing H1 title",
            tier=ValidationTier.TIER1,
        )
    elif len(h1_sections) > 1:
        result.add_issue(
            "BRD-E007",
            file_path=file_path,
            context=f"Multiple H1 headings found ({len(h1_sections)})",
            tier=ValidationTier.TIER1,
        )
    else:
        h1_text = h1_sections[0][0]
        h1_line = h1_sections[0][1]

        # Skip strict validation for templates
        if "TEMPLATE" not in str(file_path).upper():
            # For section-based layout, allow "# Section N:" or "# BRD-NN:" format
            if is_section_layout:
                section_h1_pattern = re.compile(r"^# (BRD-\d{2,}:|Section \d+:)")
                if not section_h1_pattern.match(h1_text):
                    result.add_issue(
                        "BRD-E001",
                        file_path=file_path,
                        line=h1_line,
                        context=f"Invalid H1 format. Expected '# BRD-NN: Title' or '# Section N:', got '{h1_text[:50]}'",
                        tier=ValidationTier.TIER1,
                    )
            elif not H1_TITLE_PATTERN.match(h1_text):
                result.add_issue(
                    "BRD-E001",
                    file_path=file_path,
                    line=h1_line,
                    context=f"Invalid H1 format. Expected '# BRD-NN: Title', got '{h1_text[:50]}'",
                    tier=ValidationTier.TIER1,
                )
        result.add_pass(f"{file_path.name}: H1 title format valid")


def _validate_required_sections(
    sections: List[Tuple[str, int]],
    file_path: Path,
    result: UnifiedValidationResult,
    profile: str,
) -> None:
    """Validate required sections by profile."""
    # Get required sections for profile
    if profile not in SECTION_PROFILES:
        result.add_issue(
            "BRD-W001",
            file_path=file_path,
            context=f"Unknown profile '{profile}', defaulting to standard",
            tier=ValidationTier.TIER2,
        )
        profile = "standard"

    required_sections = SECTION_PROFILES[profile]

    # Extract header texts
    section_headers = [s[0] for s in sections]

    # Check each required section (skip H1, already checked)
    missing_count = 0
    for pattern, section_name in required_sections[1:]:
        found = any(pattern.match(h) for h in section_headers)
        if not found:
            result.add_issue(
                "BRD-E006",
                file_path=file_path,
                context=f"Missing required section: {section_name}",
                tier=ValidationTier.TIER1,
            )
            missing_count += 1

    if missing_count == 0:
        result.add_pass(f"{file_path.name}: All {len(required_sections) - 1} required sections present")


def _validate_section_numbering(
    sections: List[Tuple[str, int]],
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """Validate section numbering sequence."""
    section_numbers: List[int] = []
    seen_numbers: set = set()

    for header, line_num in sections:
        match = SECTION_NUMBER_PATTERN.match(header)
        if match:
            num = int(match.group(1))

            # Check for duplicates
            if num in seen_numbers:
                result.add_issue(
                    "BRD-E008",
                    file_path=file_path,
                    line=line_num,
                    context=f"Duplicate section number: {num}",
                    tier=ValidationTier.TIER1,
                )
            else:
                seen_numbers.add(num)
                section_numbers.append(num)

    # Check for sequential numbering
    if section_numbers:
        expected = list(range(section_numbers[0], section_numbers[0] + len(section_numbers)))
        if section_numbers != expected:
            result.add_issue(
                "BRD-W001",
                file_path=file_path,
                context="Section numbers not sequential",
                tier=ValidationTier.TIER2,
            )


def _validate_document_control(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
    is_section_layout: bool = False,
) -> None:
    """Validate Document Control section."""
    # For section-based layout, accept either "## Document Control" or "## 0. Document Control"
    if is_section_layout:
        doc_control_match = re.search(
            r"## (?:0\. )?Document Control.*?(?=## \d+\.|\Z|---)",
            content,
            re.DOTALL,
        )
    else:
        doc_control_match = re.search(
            r"## 0\. Document Control.*?(?=## \d+\.|\Z)",
            content,
            re.DOTALL,
        )

    if not doc_control_match:
        result.add_issue(
            "BRD-E002",
            file_path=file_path,
            context="Missing Section 0: Document Control",
            tier=ValidationTier.TIER1,
        )
        return

    doc_control = doc_control_match.group(0)

    # Check for required fields
    missing_fields = []
    for field in DOCUMENT_CONTROL_FIELDS:
        if field not in doc_control:
            missing_fields.append(field)

    if missing_fields:
        result.add_issue(
            "BRD-E009",
            file_path=file_path,
            context=f"Document Control missing fields: {', '.join(missing_fields)}",
            tier=ValidationTier.TIER1,
        )
    else:
        result.add_pass(f"{file_path.name}: Document Control complete")


def _validate_business_requirements(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
    profile: str,
) -> None:
    """Validate Business Requirements section structure."""
    if profile == "mvp":
        # MVP: Section 6. Functional Requirements
        pattern = r"## 6\. Functional Requirements.*?(?=## \d+\.|\Z)"
        section_name = "Section 6: Functional Requirements"
    else:
        # Standard: Section 3. Business Requirements
        pattern = r"## 3\. Business Requirements.*?(?=## \d+\.|\Z)"
        section_name = "Section 3: Business Requirements"

    brd_section_match = re.search(pattern, content, re.DOTALL)

    if not brd_section_match:
        result.add_issue(
            "BRD-E011",
            file_path=file_path,
            context=f"Missing {section_name}",
            tier=ValidationTier.TIER1,
        )
        return

    brd_section = brd_section_match.group(0)

    # Check for requirement structures (tables or bullets)
    has_req_table = "|" in brd_section and ("Requirement" in brd_section or "ID" in brd_section)
    has_req_bullets = re.search(r"^\s*[-*]\s+", brd_section, re.MULTILINE)

    if not (has_req_table or has_req_bullets):
        result.add_issue(
            "BRD-W001",
            file_path=file_path,
            context=f"{section_name} lacks structured requirements (no tables or bullet lists)",
            tier=ValidationTier.TIER2,
        )
