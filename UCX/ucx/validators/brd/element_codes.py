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


def _is_definition_context(line: str) -> bool:
    """
    Determine if element ID appears in a definition context (not a reference).

    Element ID definitions appear in specific patterns:
    - Heading format: ### BRD.01.01.01: Title
    - Bold definition format at line start: **BRD.01.09.01**: Description
    - Bullet with bold definition: - **BRD.01.09.01**: Description

    Everything else (inline references, table cells, parenthetical mentions)
    is treated as a reference context.

    Args:
        line: Current line content

    Returns:
        True if this line contains element ID definitions
    """
    stripped = line.strip()

    # Heading definition: ### BRD.01.01.01: Title
    if re.match(r'^#{2,4}\s+BRD\.\d{2,}\.\d{2}\.\d{2,}:', stripped):
        return True

    # Bold definition at start: **BRD.01.01.01**: Description
    if re.match(r'^\*\*BRD\.\d{2,}\.\d{2}\.\d{2,}\*\*:', stripped):
        return True

    # Bullet with bold definition: - **BRD.01.01.01**: Description
    if re.match(r'^[-*]\s+\*\*BRD\.\d{2,}\.\d{2}\.\d{2,}\*\*:', stripped):
        return True

    return False


def _is_reference_context(
    file_path: Path,
    current_section: Optional[str],
    line: str,
) -> bool:
    """
    Determine if element ID appears in a reference context (not a definition).

    Reference contexts are determined by exclusion:
    - If line contains a definition pattern, it's NOT a reference context
    - Everything else (tables, inline mentions, parenthetical refs) is a reference

    Args:
        file_path: Path to file
        current_section: Current section number (e.g., "16.1")
        line: Current line content

    Returns:
        True if this is a reference context where IDs should not trigger duplicates
    """
    # Check filename for known reference-only files
    if "traceability" in file_path.name.lower():
        return True
    if "index" in file_path.name.lower():
        return True

    # Check if in Section 16 (Traceability section)
    if current_section and current_section.startswith("16"):
        return True

    # Check if this line contains a definition (if so, NOT a reference context)
    if _is_definition_context(line):
        return False

    # Check if line is a table row (markdown table)
    stripped_line = line.strip()
    if stripped_line.startswith("|"):
        return True

    # Check for inline reference patterns (parenthetical mentions)
    # e.g., "requires intelligent orchestration (BRD.01.23.01)"
    if re.search(r'\(BRD\.\d{2,}\.\d{2}\.\d{2,}\)', line):
        return True

    # Check for "Related Requirements" style references
    # e.g., "- BRD.01.01.01 (Platform Architecture): Technology serves..."
    if re.match(r'^[-*]\s+BRD\.\d{2,}\.\d{2}\.\d{2,}\s+\(', stripped_line):
        return True

    # Check for constraint/driver reference patterns
    # e.g., "- Must operate within ~$2M seed runway (BRD.01.03.01)"
    if re.search(r'[-*]\s+.*\(BRD\.\d{2,}\.\d{2}\.\d{2,}\)', line):
        return True

    # Check for inline constraint references with colon
    # e.g., "- BRD.02.03.02: Limited operations team capacity"
    # e.g., "BRD.02.03.01: Partner API rate limits vary by provider"
    if re.match(r'^[-*]?\s*BRD\.\d{2,}\.\d{2}\.\d{2,}:', stripped_line):
        return True

    # Check for Business Driver/Constraint inline references
    # e.g., "**Business Driver**: BRD.02.23.01 (Reduce operational overhead)"
    if re.search(r'\*\*Business (Driver|Constraint)[s]?\*\*:.*BRD\.\d{2,}\.\d{2}\.\d{2,}', line):
        return True

    # Check for "Related Requirements" section references
    # e.g., "- BRD.02.01.01-05 (All Partners): Webhook event sources"
    # e.g., "- BRD.02.01.01, 03, 04 (Partners): Settlement file sources"
    if re.match(r'^[-*]\s+BRD\.\d{2,}\.\d{2}\.\d{2,}', stripped_line):
        return True

    # Category reference lists (ID followed by description in parentheses)
    # e.g., "- Compliance BRDs: BRD.03.01.01 (Audit Trail...)"
    # e.g., "- Quality Attributes: BRD.03.02.01 (Performance...)"
    if re.search(r'BRD\.\d{2,}\.\d{2}\.\d{2,}\s*\([^)]+\)', line):
        return True

    # Multiple IDs on same line (likely a reference list)
    # e.g., "BRD.03.01.01, BRD.03.01.07, BRD.03.01.09"
    ids_in_line = ELEMENT_ID_PATTERN.findall(line)
    if len(ids_in_line) > 1:
        return True

    # Range notation for element IDs
    # e.g., "BRD.03.32.01-11" or "BRD.03.01.01-05"
    if re.search(r'BRD\.\d{2,}\.\d{2}\.\d{2,}-\d+', line):
        return True

    # Review report files are references, not definitions
    if "_review_report" in str(file_path).lower():
        return True

    return False


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

    Note: Duplicate detection is skipped for traceability sections/files where
    element IDs appear as references in cross-reference matrices.

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

        # Check if this line is in a traceability context
        is_reference = _is_reference_context(file_path, current_section, line)

        # Find element IDs in line
        for match in ELEMENT_ID_PATTERN.finditer(line):
            full_id = match.group(0)
            doc_num = match.group(1)
            type_code = match.group(2)
            seq_num = match.group(3)

            # Check for duplicate IDs (skip in traceability contexts)
            if not is_reference:
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

            # Check if type code is valid (always check, even in traceability)
            if type_code not in VALID_BRD_CODES:
                result.add_issue(
                    "BRD-E020",
                    file_path=file_path,
                    line=line_no,
                    context=f"Invalid type code '{type_code}' in {full_id}",
                    tier=ValidationTier.TIER1,
                )
                continue

            # Check section-element semantic mapping (skip in traceability contexts)
            if not is_reference:
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
