"""BRD element code validation.

Validates:
- BRD element IDs follow BRD.NN.TT.SS pattern
- Element type code TT is valid for BRD artifacts
- Section-element semantic mapping is enforced
- Legacy ID patterns are detected and warned
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ucx.validators.common.result import (
    UnifiedValidationResult,
    ValidationTier,
)
from ucx.validators.brd.schema import (
    ELEMENT_ID_PATTERN,
    SECTION_HEADING_PATTERN,
    VALID_BRD_CODES,
    SECTION_CODE_MAP,
    PREFERRED_SECTION_CODES,
    LEGACY_ID_PATTERNS,
    ELEMENT_CODE_DESCRIPTIONS,
)


def find_section_key(current_section: Optional[str]) -> Optional[str]:
    """
    Find the section key in SECTION_CODE_MAP.

    Args:
        current_section: Current section number (e.g., "7.2.1")

    Returns:
        Matching key from SECTION_CODE_MAP or None
    """
    if not current_section:
        return None

    # Try exact match first
    if current_section in SECTION_CODE_MAP:
        return current_section

    # Try parent section (e.g., "7.2" for "7.2.1")
    parts = current_section.split(".")
    for i in range(len(parts), 0, -1):
        key = ".".join(parts[:i])
        if key in SECTION_CODE_MAP:
            return key

    return None


def validate_element_codes(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """
    Validate BRD element codes.

    Checks:
    - Element IDs follow BRD.NN.TT.SS pattern
    - Type code TT is valid for BRD
    - Section-element semantic mapping
    - Legacy ID patterns

    Args:
        content: File content
        file_path: Path to file
        result: Result to populate
    """
    current_section: Optional[str] = None
    in_code_block = False
    seen_ids: Dict[str, int] = {}  # Track element IDs for duplicate detection
    lines = content.splitlines()

    for line_no, line in enumerate(lines, start=1):
        # Toggle code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip content inside code blocks
        if in_code_block:
            continue

        # Track current section
        section_match = SECTION_HEADING_PATTERN.match(line)
        if section_match:
            current_section = section_match.group(1)

        # Find element IDs in line
        for match in ELEMENT_ID_PATTERN.finditer(line):
            full_id = match.group(0)
            doc_num = match.group(1)
            type_code = match.group(2)
            seq_num = match.group(3)

            # Check for duplicate IDs
            if full_id in seen_ids:
                result.add_issue(
                    "GATE-E008",
                    file_path=file_path,
                    line=line_no,
                    context=f"Duplicate element ID: {full_id} (first seen at line {seen_ids[full_id]})",
                    tier=ValidationTier.TIER1,
                )
            else:
                seen_ids[full_id] = line_no

            # Check if type code is valid
            if type_code not in VALID_BRD_CODES:
                result.add_issue(
                    "BRD-E020",
                    file_path=file_path,
                    line=line_no,
                    context=f"Invalid type code '{type_code}' in {full_id}",
                    tier=ValidationTier.TIER1,
                )
                continue

            # Check section-element semantic mapping
            section_key = find_section_key(current_section)
            if section_key and section_key in SECTION_CODE_MAP:
                expected = SECTION_CODE_MAP[section_key]
                valid_codes = expected if isinstance(expected, set) else {expected}

                if type_code not in valid_codes:
                    codes_str = " or ".join(
                        f"'{c}' ({ELEMENT_CODE_DESCRIPTIONS.get(c, 'Unknown')})"
                        for c in sorted(valid_codes)
                    )
                    result.add_issue(
                        "GATE-W008",
                        file_path=file_path,
                        line=line_no,
                        context=f"Section {section_key} expects {codes_str}, found '{type_code}'",
                        tier=ValidationTier.TIER2,
                    )

                # Check preferred code usage
                preferred = PREFERRED_SECTION_CODES.get(section_key)
                if preferred and type_code in valid_codes and type_code != preferred:
                    result.add_issue(
                        "BRD-W023",
                        file_path=file_path,
                        line=line_no,
                        context=f"Section {section_key} prefers '{preferred}', found legacy '{type_code}'",
                        tier=ValidationTier.TIER2,
                    )

    # Check for legacy ID patterns
    _check_legacy_patterns(content, file_path, result)

    # Report valid element count
    if seen_ids:
        result.add_pass(f"{file_path.name}: Found {len(seen_ids)} valid element IDs")
        result.metadata.setdefault("element_counts", {})[str(file_path)] = len(seen_ids)


def _check_legacy_patterns(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """
    Check for legacy (non-unified) element ID patterns.

    Args:
        content: File content
        file_path: Path to file
        result: Result to populate
    """
    in_code_block = False
    lines = content.splitlines()

    for line_no, line in enumerate(lines, start=1):
        # Toggle code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        for pattern_name, pattern in LEGACY_ID_PATTERNS.items():
            matches = pattern.findall(line)
            for match in matches:
                result.add_issue(
                    "BRD-W002",
                    file_path=file_path,
                    line=line_no,
                    context=f"Legacy ID pattern '{match}' should use BRD.NN.TT.SS format",
                    tier=ValidationTier.TIER2,
                )
