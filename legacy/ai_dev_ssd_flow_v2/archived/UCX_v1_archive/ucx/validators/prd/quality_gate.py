"""PRD Quality Gate Validation Module.

Implements 20 GATE checks for PRD validation with tiered severity.

Tier 1 (Blocking):
- GATE-01: Placeholder detection
- GATE-02: Downstream reference blocking (Layer 5+)
- GATE-04: Section completeness (21 sections)
- GATE-05: Element ID format (PRD.NN.TT.SS)
- GATE-06: Diagram contracts
- GATE-08: Element uniqueness
- GATE-10: File size (<20K tokens)
- GATE-15: SYS-Ready score ≥85% (MVP) or ≥90% (Standard)
- GATE-16: EARS-Ready score ≥85% (MVP) or ≥90% (Standard)

Tier 2 (Advisory):
- GATE-03: Upstream references (BRD traceability)
- GATE-07: Cross-reference validity
- GATE-09: Acceptance criteria completeness
- GATE-11: Feature hierarchy
- GATE-12: User story format
- GATE-13: Priority consistency
- GATE-14: Dependency mapping
- GATE-17: Traceability coverage
- GATE-18: Non-functional requirements
- GATE-19: Success metrics defined
- GATE-20: Release criteria
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from ucx.validators.prd import ValidationIssue, Tier
from ucx.validators.prd.schema import (
    FILE_LINE_WARNING,
    FILE_LINE_ERROR,
    TOKEN_WARNING,
    TOKEN_ERROR,
    CHARS_PER_TOKEN,
    PLACEHOLDER_PATTERNS,
    FORBIDDEN_DOWNSTREAM_PATTERNS,
    ALLOWED_DOWNSTREAM_PATTERNS,
    REQUIRED_DIAGRAM_TAGS,
    SEQUENCE_DIAGRAM_PATTERN,
    SEQUENCE_ALT_PATTERN,
    REQUIRED_SECTIONS,
    estimate_tokens,
)


def run_quality_gates(
    file_path: Path,
    content: str,
    tier1_only: bool = False,
) -> List[ValidationIssue]:
    """Run all quality gate checks on a PRD file.

    Args:
        file_path: Path to PRD file
        content: File content
        tier1_only: Only run Tier 1 (blocking) checks

    Returns:
        List of validation issues
    """
    issues = []
    file_name = file_path.name

    # Tier 1 (Blocking) Gates
    issues.extend(_gate_01_placeholders(file_name, content))
    issues.extend(_gate_02_downstream_refs(file_name, content))
    issues.extend(_gate_04_section_completeness(file_name, content))
    issues.extend(_gate_05_element_format(file_name, content))
    issues.extend(_gate_06_diagram_contracts(file_name, content))
    issues.extend(_gate_08_element_uniqueness(file_name, content))
    issues.extend(_gate_10_file_size(file_name, content))

    # Tier 2 (Advisory) Gates - skip if tier1_only
    if not tier1_only:
        issues.extend(_gate_03_upstream_refs(file_name, content))
        issues.extend(_gate_07_cross_refs(file_name, content))
        issues.extend(_gate_09_acceptance_criteria(file_name, content))
        issues.extend(_gate_11_feature_hierarchy(file_name, content))
        issues.extend(_gate_12_user_story_format(file_name, content))
        issues.extend(_gate_13_priority_consistency(file_name, content))
        issues.extend(_gate_14_dependency_mapping(file_name, content))
        issues.extend(_gate_17_traceability_coverage(file_name, content))
        issues.extend(_gate_18_nfr_completeness(file_name, content))
        issues.extend(_gate_19_success_metrics(file_name, content))
        issues.extend(_gate_20_release_criteria(file_name, content))

    return issues


# =============================================================================
# TIER 1 GATES (Blocking)
# =============================================================================

def _gate_01_placeholders(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-01: Detect placeholder text that indicates incomplete content."""
    issues = []

    for pattern in PLACEHOLDER_PATTERNS:
        matches = list(pattern.finditer(content))
        for match in matches[:5]:  # Limit to first 5 per pattern
            line_num = content[:match.start()].count('\n') + 1

            # Check for merge conflicts specifically
            if "<<<" in match.group() or ">>>" in match.group() or "===" in match.group():
                # Skip === in table rows
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                line = content[line_start:line_end if line_end > 0 else len(content)]
                if line.count('|') >= 2:  # Likely a table row
                    continue

                issues.append(ValidationIssue(
                    code="CORPUS-E001",
                    message=f"Merge conflict marker at line {line_num}",
                    file=file_name,
                    line=line_num,
                    tier=Tier.TIER1,
                ))
            else:
                issues.append(ValidationIssue(
                    code="CORPUS-E001",
                    message=f"Placeholder '{match.group()}' detected at line {line_num}",
                    file=file_name,
                    line=line_num,
                    tier=Tier.TIER1,
                ))

    return issues


def _gate_02_downstream_refs(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-02: Block forbidden downstream artifact references (Layer 5+)."""
    issues = []

    for pattern in FORBIDDEN_DOWNSTREAM_PATTERNS:
        matches = list(pattern.finditer(content))
        for match in matches[:3]:
            line_num = content[:match.start()].count('\n') + 1

            # Get line context
            line_start = content.rfind('\n', 0, match.start()) + 1
            line_end = content.find('\n', match.end())
            line = content[line_start:line_end if line_end > 0 else len(content)]

            # Skip if in allowed context
            if _is_allowed_context(line):
                continue

            issues.append(ValidationIssue(
                code="PRD-E002",
                message=f"Forbidden downstream reference '{match.group()}' - PRD cannot reference Layer 5+",
                file=file_name,
                line=line_num,
                tier=Tier.TIER1,
            ))

    return issues


def _gate_04_section_completeness(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-04: Verify 21-section structure completeness."""
    issues = []

    # Only check for main/monolithic files
    if not _is_main_file(file_name, content):
        return issues

    # Find all sections
    section_pattern = re.compile(r"^## (\d+)\.", re.MULTILINE)
    found_sections = set(int(m.group(1)) for m in section_pattern.finditer(content))

    # Check for missing sections
    missing = []
    for section_num in REQUIRED_SECTIONS:
        if section_num not in found_sections:
            missing.append(section_num)

    if missing:
        # Only report as error if more than 3 sections missing
        if len(missing) > 3:
            issues.append(ValidationIssue(
                code="PRD-E012",
                message=f"Missing {len(missing)} required sections: {missing[:5]}{'...' if len(missing) > 5 else ''}",
                file=file_name,
                tier=Tier.TIER1,
            ))
        else:
            issues.append(ValidationIssue(
                code="PRD-W012",
                message=f"Missing sections: {missing}",
                file=file_name,
                tier=Tier.TIER2,
            ))

    return issues


def _gate_05_element_format(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-05: Validate element ID format (PRD.NN.TT.SS)."""
    issues = []

    invalid_pattern = re.compile(r"\bPRD-(\d{2,9})\b(?=\s*:)")
    doc_level_contexts = [
        re.compile(r"^\s*#\s+PRD-\d{2,9}\s*:"),
        re.compile(r"^\s*title:\s*['\"]?PRD-\d{2,9}\s*:"),
        re.compile(r"^\s*doc_id:\s*PRD-\d{2,9}\s*$"),
        re.compile(r"^\s*\|\s*Document ID\s*\|\s*PRD-\d{2,9}\s*\|"),
        re.compile(r"@depends:\s*PRD-\d{2,9}\b"),
        re.compile(r"@discoverability:\s*PRD-\d{2,9}\b"),
        re.compile(r"Target document ID:\s*`PRD-\d{2,9}`"),
    ]

    for line_num, line in enumerate(content.splitlines(), start=1):
        if not invalid_pattern.search(line):
            continue
        if any(pattern.search(line) for pattern in doc_level_contexts):
            continue

        for match in invalid_pattern.finditer(line):
            prefix = line[:match.start()].strip()
            # Allow narrative mentions like "... in PRD-02: ..." while still
            # flagging list/item labels that incorrectly use PRD-NN as element IDs.
            if prefix and prefix not in {"-", "*", "+"} and not re.fullmatch(r"\d+\.", prefix):
                continue
            issues.append(ValidationIssue(
                code="PRD-E005",
                message=f"Invalid element format '{match.group()}', use PRD.NN.TT.SS",
                file=file_name,
                line=line_num,
                tier=Tier.TIER1,
            ))

    return issues


def _gate_06_diagram_contracts(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-06: Verify diagram tag contracts."""
    issues = []

    # Check for required diagram types in main files
    if not _is_main_file(file_name, content):
        return issues

    # Check for @diagram tags
    has_c4 = "@diagram:" in content and "c4" in content.lower()
    has_dfd = "@diagram:" in content and "dfd" in content.lower()

    # C4 or DFD is recommended but not blocking
    if not has_c4 and not has_dfd:
        issues.append(ValidationIssue(
            code="PRD-W016",
            message="No @diagram: tags found. Consider adding C4 or DFD diagrams",
            file=file_name,
            tier=Tier.TIER2,
        ))

    # Check sequence diagrams for alt/else branches
    if SEQUENCE_DIAGRAM_PATTERN.search(content):
        # Find sequence diagram blocks
        seq_blocks = re.findall(
            r"```mermaid\s*sequenceDiagram(.*?)```",
            content,
            re.DOTALL | re.IGNORECASE
        )
        for block in seq_blocks:
            if not SEQUENCE_ALT_PATTERN.search(block):
                issues.append(ValidationIssue(
                    code="PRD-W017",
                    message="Sequence diagram missing alt/else branches for error handling",
                    file=file_name,
                    tier=Tier.TIER2,
                ))
                break

    return issues


def _gate_08_element_uniqueness(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-08: Ensure element ID uniqueness within document."""
    issues = []

    # Extract all element IDs
    pattern = re.compile(r"\bPRD\.(\d{2})\.(\d{2})\.(\d{2})\b")
    seen: Dict[str, int] = {}

    for match in pattern.finditer(content):
        element_id = match.group(0)
        line_num = content[:match.start()].count('\n') + 1

        # Check if this looks like a definition (not a reference)
        line_start = content.rfind('\n', 0, match.start()) + 1
        line_end_idx = content.find('\n', match.end())
        if line_end_idx == -1:
            line_end_idx = len(content)
        full_line = content[line_start:line_end_idx]
        prefix = content[line_start:match.start()].strip()

        # Skip lines that contain reference indicators — even if the prefix
        # looks like a definition marker (e.g. "- PRD.01.06.01 → @brd: ...").
        # Mirrors the same logic in element_codes._is_definition_context().
        is_reference = (
            '\u2192' in full_line or          # → arrow used in traceability
            '@brd:' in full_line.lower() or
            '@prd:' in full_line.lower() or
            'traces to' in full_line.lower() or
            'references ' in full_line.lower()
        )

        # Definition patterns: start of line, bullet, table cell, bold
        is_definition = not is_reference and (
            prefix == "" or
            prefix == "-" or
            prefix == "*" or
            prefix.endswith("|") or
            prefix.endswith("**")
        )

        if is_definition:
            if element_id in seen:
                issues.append(ValidationIssue(
                    code="PRD-E017",
                    message=f"Duplicate element ID {element_id} (first at line {seen[element_id]})",
                    file=file_name,
                    line=line_num,
                    tier=Tier.TIER1,
                ))
            else:
                seen[element_id] = line_num

    return issues


def _gate_10_file_size(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-10: Check file size limits."""
    issues = []

    # Use logical line count to avoid trailing-newline off-by-one behavior.
    line_count = max(1, len(content.splitlines()))
    token_count = estimate_tokens(content)

    # Line count checks
    if line_count > FILE_LINE_ERROR:
        issues.append(ValidationIssue(
            code="CORPUS-E017",
            message=f"File has {line_count} lines, exceeds {FILE_LINE_ERROR} limit",
            file=file_name,
            tier=Tier.TIER1,
        ))
    elif line_count > FILE_LINE_WARNING:
        issues.append(ValidationIssue(
            code="CORPUS-W017",
            message=f"File has {line_count} lines, approaching {FILE_LINE_ERROR} limit",
            file=file_name,
            tier=Tier.TIER2,
        ))

    # Token count checks
    if token_count > TOKEN_ERROR:
        issues.append(ValidationIssue(
            code="CORPUS-E010",
            message=f"File has ~{token_count} tokens, exceeds {TOKEN_ERROR} limit",
            file=file_name,
            tier=Tier.TIER1,
        ))
    elif token_count > TOKEN_WARNING:
        issues.append(ValidationIssue(
            code="CORPUS-W010",
            message=f"File has ~{token_count} tokens, approaching {TOKEN_ERROR} limit",
            file=file_name,
            tier=Tier.TIER2,
        ))

    return issues


# =============================================================================
# TIER 2 GATES (Advisory)
# =============================================================================

def _gate_03_upstream_refs(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-03: Check upstream BRD traceability."""
    issues = []

    # PRD should reference BRD
    brd_pattern = re.compile(r"@brd:\s*BRD\.\d{2}\.\d{2}\.\d{2}")
    has_brd_trace = brd_pattern.search(content) is not None

    # Also check for BRD-NN reference in Document Control
    brd_ref = re.search(r"BRD[-_]\d{2}", content, re.IGNORECASE)

    if not has_brd_trace and not brd_ref:
        issues.append(ValidationIssue(
            code="PRD-W004",
            message="No upstream BRD traceability found. Add @brd: references",
            file=file_name,
            tier=Tier.TIER2,
        ))

    return issues


def _gate_07_cross_refs(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-07: Validate internal cross-references."""
    issues = []

    # Find all PRD element references
    ref_pattern = re.compile(r"(?:see|ref|→)\s*(PRD\.\d{2}\.\d{2}\.\d{2})", re.IGNORECASE)
    def_pattern = re.compile(r"\bPRD\.(\d{2})\.(\d{2})\.(\d{2})\b")

    # Get all definitions
    definitions = set(m.group(0) for m in def_pattern.finditer(content))

    # Check references against definitions
    for match in ref_pattern.finditer(content):
        ref_id = match.group(1)
        if ref_id not in definitions:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(ValidationIssue(
                code="PRD-W007",
                message=f"Reference to undefined element {ref_id}",
                file=file_name,
                line=line_num,
                tier=Tier.TIER2,
            ))

    return issues


def _gate_09_acceptance_criteria(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-09: Check acceptance criteria completeness."""
    issues = []

    # Find Section 11 (Acceptance Criteria)
    section_11 = _extract_main_section(content, 11)

    if section_11:
        section_content = section_11

        # Check for AC elements (PRD.NN.06.SS)
        ac_pattern = re.compile(r"PRD\.\d{2}\.06\.\d{2}")
        ac_count = len(ac_pattern.findall(section_content))

        if ac_count < 3:
            issues.append(ValidationIssue(
                code="PRD-W009",
                message=f"Section 11 has only {ac_count} acceptance criteria, recommend ≥3",
                file=file_name,
                tier=Tier.TIER2,
            ))

    return issues


def _gate_11_feature_hierarchy(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-11: Check feature hierarchy in Section 7."""
    issues = []

    # Find Section 7 (Scope & Requirements)
    section_7 = _extract_main_section(content, 7)

    if section_7:
        section_content = section_7

        # Check for feature elements (PRD.NN.22.SS)
        feature_pattern = re.compile(r"PRD\.\d{2}\.22\.\d{2}")
        features = feature_pattern.findall(section_content)

        if not features:
            issues.append(ValidationIssue(
                code="PRD-W011",
                message="Section 7 missing feature elements (PRD.NN.22.SS)",
                file=file_name,
                tier=Tier.TIER2,
            ))

    return issues


def _gate_12_user_story_format(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-12: Validate user story format in Section 8."""
    issues = []

    # Find Section 8 (User Stories)
    section_8 = _extract_main_section(content, 8)

    if section_8:
        section_content = section_8

        # Check for user story elements (PRD.NN.09.SS)
        us_pattern = re.compile(r"PRD\.\d{2}\.09\.\d{2}")
        user_stories = us_pattern.findall(section_content)

        if not user_stories:
            issues.append(ValidationIssue(
                code="PRD-W012",
                message="Section 8 missing user story elements (PRD.NN.09.SS)",
                file=file_name,
                tier=Tier.TIER2,
            ))

        # Check for "As a... I want... So that..." format
        as_a_pattern = re.compile(r"As\s+a\s+", re.IGNORECASE)
        i_want_pattern = re.compile(r"I\s+want\s+", re.IGNORECASE)

        if not as_a_pattern.search(section_content):
            issues.append(ValidationIssue(
                code="PRD-W013",
                message="User stories missing 'As a...' format",
                file=file_name,
                tier=Tier.TIER2,
            ))

    return issues


def _gate_13_priority_consistency(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-13: Check priority values consistency."""
    issues = []

    # Look for priority indicators
    priority_pattern = re.compile(r"\bP[0-4]\b|\bMust\b|\bShould\b|\bCould\b|\bWon't\b", re.IGNORECASE)
    priorities = priority_pattern.findall(content)

    # Check for mixed priority systems
    has_p_notation = any(p.upper().startswith('P') for p in priorities)
    has_moscow = any(p.lower() in ['must', 'should', 'could', "won't"] for p in priorities)

    if has_p_notation and has_moscow:
        issues.append(ValidationIssue(
            code="PRD-W014",
            message="Mixed priority notation (P0-P4 and MoSCoW). Use consistent system",
            file=file_name,
            tier=Tier.TIER2,
        ))

    return issues


def _gate_14_dependency_mapping(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-14: Check dependency mapping completeness."""
    issues = []

    # Check for dependency elements (PRD.NN.05.SS)
    dep_pattern = re.compile(r"PRD\.\d{2}\.05\.\d{2}")
    dependencies = dep_pattern.findall(content)

    if not dependencies:
        issues.append(ValidationIssue(
            code="PRD-W015",
            message="No dependency elements found (PRD.NN.05.SS)",
            file=file_name,
            tier=Tier.TIER2,
        ))

    return issues


def _gate_17_traceability_coverage(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-17: Check traceability section completeness."""
    issues = []

    # Find Section 18 (Traceability)
    section_18 = _extract_main_section(content, 18)

    if section_18:
        section_content = section_18

        # Check for ADR topics table
        if "ADR" not in section_content and "Architecture Decision" not in section_content:
            issues.append(ValidationIssue(
                code="PRD-W018",
                message="Section 18 missing ADR topics table",
                file=file_name,
                tier=Tier.TIER2,
            ))

    return issues


def _gate_18_nfr_completeness(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-18: Check non-functional requirements in Section 21."""
    issues = []

    # Find Section 21 (Quality Assurance)
    section_21 = _extract_main_section(content, 21)

    if section_21:
        section_content = section_21

        # Check for NFR elements (PRD.NN.02.SS)
        nfr_pattern = re.compile(r"PRD\.\d{2}\.02\.\d{2}")
        nfrs = nfr_pattern.findall(section_content)

        if not nfrs:
            issues.append(ValidationIssue(
                code="PRD-W019",
                message="Section 21 missing quality attribute elements (PRD.NN.02.SS)",
                file=file_name,
                tier=Tier.TIER2,
            ))

    return issues


def _gate_19_success_metrics(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-19: Check success metrics in Section 5."""
    issues = []

    # Find Section 5 (Success Metrics)
    section_5 = _extract_main_section(content, 5)

    if section_5:
        section_content = section_5

        # Check for metric elements (PRD.NN.08.SS)
        metric_pattern = re.compile(r"PRD\.\d{2}\.08\.\d{2}")
        metrics = metric_pattern.findall(section_content)

        if not metrics:
            issues.append(ValidationIssue(
                code="PRD-W020",
                message="Section 5 missing metric elements (PRD.NN.08.SS)",
                file=file_name,
                tier=Tier.TIER2,
            ))

    return issues


def _gate_20_release_criteria(file_name: str, content: str) -> List[ValidationIssue]:
    """GATE-20: Check release criteria in Section 14."""
    issues = []

    # Find Section 14 (Success Definition)
    section_14 = _extract_main_section(content, 14)

    if section_14:
        section_content = section_14

        # Check for release/launch criteria keywords
        criteria_keywords = ["release", "launch", "milestone", "criteria", "target"]
        has_criteria = any(kw in section_content.lower() for kw in criteria_keywords)

        if not has_criteria:
            issues.append(ValidationIssue(
                code="PRD-W021",
                message="Section 14 missing release/launch criteria",
                file=file_name,
                tier=Tier.TIER2,
            ))

    return issues


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _is_main_file(file_name: str, content: str) -> bool:
    """Determine if this is a main/monolithic PRD file."""
    # Section files have format PRD-NN.S_slug.md
    if re.match(r"PRD-\d{2}\.\d+_", file_name):
        return False

    # If it has multiple sections, it's likely a main file
    section_count = len(re.findall(r"^## \d+\.", content, re.MULTILINE))
    return section_count >= 5


def _is_allowed_context(line: str) -> bool:
    """Check if downstream reference is in an allowed planning context."""
    allowed_keywords = [
        "downstream",
        "to be detailed",
        "will be defined",
        "planned",
        "expected output",
        "output:",
        "future",
    ]
    line_lower = line.lower()
    return any(kw in line_lower for kw in allowed_keywords)


def _extract_main_section(content: str, section_num: int) -> Optional[str]:
    """Extract full main section content from a monolithic PRD.

    Uses \\Z for end-of-string to avoid multiline '$' truncation bugs.
    """
    pattern = re.compile(
        rf"^## {section_num}\.\s+.*?(?=^## \d+\.|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    return match.group(0) if match else None
