"""PRD Element Code Validation Module.

Validates:
- PRD.NN.TT.SS format (4-segment element IDs)
- Type code validity (13 valid codes: 01-09, 11, 22, 23, 24)
- Section-type alignment
- Element uniqueness
- Context detection (definition vs reference)
- Upstream traceability (@brd: format)
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass

from ucx.validators.prd import ValidationIssue, Tier
from ucx.validators.prd.schema import (
    VALID_TYPE_CODES,
    TYPE_CODE_DESCRIPTIONS,
    TYPE_CODE_PRIMARY_SECTION,
    SECTION_CODE_MAP,
    PRD_ELEMENT_ID_PATTERN,
    PRD_ELEMENT_ID_EXTRACT,
    LEGACY_PATTERN_COMPILED,
    FORBIDDEN_DOWNSTREAM_PATTERNS,
)


@dataclass
class ElementContext:
    """Context information for an element ID occurrence."""

    element_id: str
    doc_num: str
    type_code: str
    seq_num: str
    line_number: int
    is_definition: bool
    section_num: Optional[int]
    context_text: str


def validate_element_codes(file_path: Path, content: str) -> List[ValidationIssue]:
    """Validate PRD element codes.

    Args:
        file_path: Path to PRD file
        content: File content

    Returns:
        List of validation issues
    """
    issues = []
    file_name = file_path.name

    # Extract all element IDs with context
    elements = _extract_elements_with_context(content)

    # Validate individual elements
    for element in elements:
        issues.extend(_validate_element(file_name, element))

    # Check for duplicates
    issues.extend(_check_duplicates(file_name, elements))

    # Check for legacy patterns
    issues.extend(_check_legacy_patterns(file_name, content))

    # Check for forbidden downstream references
    issues.extend(_check_downstream_refs(file_name, content))

    return issues


def _extract_elements_with_context(content: str) -> List[ElementContext]:
    """Extract all PRD element IDs with their context information."""
    elements = []
    lines = content.split('\n')

    current_section = None
    section_pattern = re.compile(r"^## (\d+)\.")

    for line_num, line in enumerate(lines, 1):
        # Track current section
        section_match = section_pattern.match(line)
        if section_match:
            current_section = int(section_match.group(1))

        # Find all PRD element IDs on this line
        for match in PRD_ELEMENT_ID_EXTRACT.finditer(line):
            doc_num = match.group(1)
            type_code = match.group(2)
            seq_num = match.group(3)
            element_id = f"PRD.{doc_num}.{type_code}.{seq_num}"

            # Determine if this is a definition or reference
            is_definition = _is_definition_context(line, match.start())

            # Get surrounding context for debugging
            start = max(0, match.start() - 20)
            end = min(len(line), match.end() + 20)
            context_text = line[start:end]

            elements.append(ElementContext(
                element_id=element_id,
                doc_num=doc_num,
                type_code=type_code,
                seq_num=seq_num,
                line_number=line_num,
                is_definition=is_definition,
                section_num=current_section,
                context_text=context_text,
            ))

    return elements


def _is_definition_context(line: str, position: int) -> bool:
    """Determine if an element ID at position is a definition or reference.

    Definitions typically appear:
    - At the start of a line (with optional markers like -, *, |)
    - In table rows as the first cell
    - With format: "**PRD.XX.XX.XX**: description"
    - In requirement blocks: "PRD.XX.XX.XX - description"

    References typically appear:
    - In @brd: or @prd: tags
    - In prose text referencing other elements
    - In traceability sections
    """
    # Get text before the ID
    prefix = line[:position].strip()

    # Definition patterns
    definition_indicators = [
        prefix == "",                           # Start of line
        prefix == "-",                          # Bullet point
        prefix == "*",                          # Bullet point
        prefix.endswith("|"),                   # Table cell start
        prefix.endswith("**"),                  # Bold definition
        prefix == "- **",                       # Bullet + bold
        re.match(r"^\s*\|?\s*$", prefix),       # Table or empty
        re.match(r"^\s*[-*]\s*$", prefix),      # List item
    ]

    # Reference patterns
    reference_indicators = [
        "@prd:" in line.lower(),
        "@brd:" in line.lower(),
        "see " in prefix.lower(),
        "references " in prefix.lower(),
        "from " in prefix.lower(),
        "traces to " in prefix.lower(),
        "→" in prefix,
    ]

    if any(reference_indicators):
        return False

    return any(definition_indicators)


def _validate_element(file_name: str, element: ElementContext) -> List[ValidationIssue]:
    """Validate a single element ID."""
    issues = []

    # Validate type code
    if element.type_code not in VALID_TYPE_CODES:
        issues.append(ValidationIssue(
            code="PRD-E013",
            message=f"Invalid type code '{element.type_code}' in {element.element_id}, "
                    f"valid codes: {', '.join(sorted(VALID_TYPE_CODES))}",
            file=file_name,
            line=element.line_number,
            tier=Tier.TIER1,
        ))
        return issues  # Skip further validation if type code is invalid

    # Validate section-type alignment (only for definitions)
    if element.is_definition and element.section_num:
        expected_codes = SECTION_CODE_MAP.get(str(element.section_num), [])
        if expected_codes and element.type_code not in expected_codes:
            type_desc = TYPE_CODE_DESCRIPTIONS.get(element.type_code, "Unknown")
            primary_section = TYPE_CODE_PRIMARY_SECTION.get(element.type_code, "?")
            issues.append(ValidationIssue(
                code="PRD-W008",
                message=f"{element.element_id} ({type_desc}) in Section {element.section_num}, "
                        f"expected in Section {primary_section}",
                file=file_name,
                line=element.line_number,
                tier=Tier.TIER2,
            ))

    # Validate sequence number format (must be 01-99)
    seq = int(element.seq_num)
    if seq < 1 or seq > 99:
        issues.append(ValidationIssue(
            code="PRD-E014",
            message=f"Invalid sequence number '{element.seq_num}' in {element.element_id}, "
                    f"must be 01-99",
            file=file_name,
            line=element.line_number,
            tier=Tier.TIER1,
        ))

    return issues


def _check_duplicates(
    file_name: str,
    elements: List[ElementContext],
) -> List[ValidationIssue]:
    """Check for duplicate element ID definitions."""
    issues = []

    # Only check definitions for duplicates
    definitions = [e for e in elements if e.is_definition]

    seen: Dict[str, ElementContext] = {}
    for element in definitions:
        if element.element_id in seen:
            first = seen[element.element_id]
            issues.append(ValidationIssue(
                code="PRD-E017",
                message=f"Duplicate element ID {element.element_id} "
                        f"(first at line {first.line_number}, duplicate at line {element.line_number})",
                file=file_name,
                line=element.line_number,
                tier=Tier.TIER1,
            ))
        else:
            seen[element.element_id] = element

    return issues


def _check_legacy_patterns(file_name: str, content: str) -> List[ValidationIssue]:
    """Check for legacy ID patterns that should be migrated."""
    issues = []

    for pattern, suggestion in LEGACY_PATTERN_COMPILED:
        matches = list(pattern.finditer(content))
        if matches:
            # Find line numbers for first 3 matches
            lines = content.split('\n')
            for match in matches[:3]:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    code="PRD-W003",
                    message=f"Legacy ID pattern '{match.group()}' found, migrate to {suggestion}",
                    file=file_name,
                    line=line_num,
                    tier=Tier.TIER2,
                ))

    return issues


def _check_downstream_refs(file_name: str, content: str) -> List[ValidationIssue]:
    """Check for forbidden downstream artifact references."""
    issues = []

    for pattern in FORBIDDEN_DOWNSTREAM_PATTERNS:
        matches = list(pattern.finditer(content))
        for match in matches[:3]:  # Limit to first 3 per pattern
            line_num = content[:match.start()].count('\n') + 1

            # Get context to check if it's in an allowed context
            line_start = content.rfind('\n', 0, match.start()) + 1
            line_end = content.find('\n', match.end())
            line = content[line_start:line_end if line_end > 0 else len(content)]

            # Skip if in allowed planning context
            if _is_allowed_downstream_context(line):
                continue

            issues.append(ValidationIssue(
                code="PRD-E002",
                message=f"Forbidden downstream reference '{match.group()}' (PRD cannot reference Layer 5+)",
                file=file_name,
                line=line_num,
                tier=Tier.TIER1,
            ))

    return issues


def _is_allowed_downstream_context(line: str) -> bool:
    """Check if downstream reference is in an allowed context."""
    allowed_contexts = [
        "downstream",       # "downstream artifacts: ADR, SYS"
        "to be detailed",   # "To be detailed in ADR"
        "will be defined",  # "Will be defined in SYS"
        "see future",       # Planning reference
        "planned",          # Planning reference
        "expected output",  # Output mapping
        "output:",          # Output section
    ]
    line_lower = line.lower()
    return any(ctx in line_lower for ctx in allowed_contexts)


def get_element_ids(content: str) -> Set[str]:
    """Extract all unique element IDs from content."""
    ids = set()
    for match in PRD_ELEMENT_ID_EXTRACT.finditer(content):
        doc_num = match.group(1)
        type_code = match.group(2)
        seq_num = match.group(3)
        ids.add(f"PRD.{doc_num}.{type_code}.{seq_num}")
    return ids


def get_element_definitions(content: str) -> Dict[str, int]:
    """Get element ID definitions with their line numbers."""
    elements = _extract_elements_with_context(content)
    return {
        e.element_id: e.line_number
        for e in elements
        if e.is_definition
    }


def get_element_references(content: str) -> Dict[str, List[int]]:
    """Get element ID references with their line numbers."""
    elements = _extract_elements_with_context(content)
    refs: Dict[str, List[int]] = {}
    for e in elements:
        if not e.is_definition:
            if e.element_id not in refs:
                refs[e.element_id] = []
            refs[e.element_id].append(e.line_number)
    return refs


def count_elements_by_type(content: str) -> Dict[str, int]:
    """Count elements by type code."""
    counts: Dict[str, int] = {}
    elements = _extract_elements_with_context(content)

    for e in elements:
        if e.is_definition:
            counts[e.type_code] = counts.get(e.type_code, 0) + 1

    return counts


def validate_element_id_format(element_id: str) -> Tuple[bool, Optional[str]]:
    """Validate a single element ID format.

    Returns:
        Tuple of (is_valid, error_message)
    """
    match = PRD_ELEMENT_ID_PATTERN.match(element_id)
    if not match:
        return False, f"Invalid format '{element_id}', expected PRD.NN.TT.SS"

    doc_num = match.group(1)
    type_code = match.group(2)
    seq_num = match.group(3)

    # Validate type code
    if type_code not in VALID_TYPE_CODES:
        return False, f"Invalid type code '{type_code}' in {element_id}"

    # Validate sequence number
    if int(seq_num) < 1 or int(seq_num) > 99:
        return False, f"Invalid sequence number '{seq_num}' in {element_id}"

    return True, None
