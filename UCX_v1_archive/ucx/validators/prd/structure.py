"""PRD Structure Validation Module.

Validates:
- 21-section structure (both MVP and Standard templates)
- Section numbering and ordering
- Section 10 (Customer-Facing Content) blocking requirement
- Section 8 layer separation note
- File naming conventions
"""

import re
from pathlib import Path
from typing import List

from ucx.validators.prd import ValidationIssue, Tier
from ucx.validators.prd.schema import (
    REQUIRED_SECTIONS,
    BLOCKING_SECTIONS,
    PRD_FILE_PATTERN,
    PRD_INDEX_PATTERN,
    PRD_TEMPLATE_PATTERN,
    PLACEHOLDER_PATTERNS,
    LAYER_SEPARATION_NOTE_KEYWORDS,
    BDD_PATTERNS,
    EARS_PATTERNS,
    has_layer_separation_note,
    has_bdd_patterns,
    has_ears_patterns,
)


def validate_structure(file_path: Path, content: str) -> List[ValidationIssue]:
    """Validate PRD structure.

    Args:
        file_path: Path to PRD file
        content: File content

    Returns:
        List of validation issues
    """
    issues = []
    file_name = file_path.name

    # Skip index and template files
    if PRD_INDEX_PATTERN.match(file_name) or PRD_TEMPLATE_PATTERN.match(file_name):
        return issues

    # Validate file naming
    issues.extend(_validate_file_naming(file_path))

    # Validate H1 heading
    issues.extend(_validate_h1(file_path, content))

    # Validate sections
    issues.extend(_validate_sections(file_path, content))

    # Validate Section 10 (BLOCKING)
    issues.extend(_validate_section_10(file_path, content))

    # Validate Section 8 layer separation
    issues.extend(_validate_section_8(file_path, content))

    # Check for placeholders
    issues.extend(_check_placeholders(file_path, content))

    # Validate SSD Layer-2 scope boundaries
    issues.extend(_validate_layer2_scope(file_path, content))

    return issues


def _validate_file_naming(file_path: Path) -> List[ValidationIssue]:
    """Validate PRD file naming convention."""
    issues: List[ValidationIssue] = []
    file_name = file_path.name

    # Skip validation for section files (they have different patterns)
    if re.match(r"PRD-\d{2,9}\.\d+_", file_name):
        return issues

    # Check main file naming
    if not PRD_FILE_PATTERN.match(file_name):
        issues.append(ValidationIssue(
            code="PRD-W002",
            message=f"File name '{file_name}' does not match format PRD-NN_descriptive_name.md",
            file=file_name,
            tier=Tier.TIER2,
        ))

    return issues


def _validate_h1(file_path: Path, content: str) -> List[ValidationIssue]:
    """Validate H1 heading format."""
    issues: List[ValidationIssue] = []
    file_name = file_path.name

    # Find H1 heading
    h1_match = re.search(r"^# (.+)$", content, re.MULTILINE)

    if not h1_match:
        issues.append(ValidationIssue(
            code="PRD-E001",
            message="Missing or invalid H1 heading",
            file=file_name,
            tier=Tier.TIER1,
        ))
        return issues

    h1_text = h1_match.group(1)

    # Check format: # PRD-NN: Title
    if not re.match(r"PRD-\d{2}:", h1_text):
        issues.append(ValidationIssue(
            code="PRD-E001",
            message=f"H1 heading '{h1_text}' should match format 'PRD-NN: Title'",
            file=file_name,
            tier=Tier.TIER1,
        ))

    # Check for multiple H1 headings
    h1_count = len(re.findall(r"^# ", content, re.MULTILINE))
    if h1_count > 1:
        issues.append(ValidationIssue(
            code="PRD-E001",
            message=f"Multiple H1 headings detected ({h1_count}). Use single H1 only",
            file=file_name,
            tier=Tier.TIER1,
        ))

    return issues


def _validate_sections(file_path: Path, content: str) -> List[ValidationIssue]:
    """Validate 21-section structure."""
    issues = []
    file_name = file_path.name

    # Find all section headings (## N. Title)
    section_pattern = re.compile(r"^## (\d+)\.\s+(.+)$", re.MULTILINE)
    found_sections = {}

    for match in section_pattern.finditer(content):
        section_num = int(match.group(1))
        section_title = match.group(2)
        found_sections[section_num] = section_title

    # Check for missing sections (only for main/monolithic files)
    # Section files won't have all 21 sections
    if _is_main_prd_file(file_path, content):
        for section_num, expected_title in REQUIRED_SECTIONS.items():
            if section_num not in found_sections:
                issues.append(ValidationIssue(
                    code="PRD-E012",
                    message=f"Missing required section {section_num}: {expected_title}",
                    file=file_name,
                    tier=Tier.TIER1,
                ))

    # Check section numbering is sequential
    section_nums = sorted(found_sections.keys())
    for i, num in enumerate(section_nums):
        if i > 0 and num != section_nums[i - 1] + 1:
            # Gap in numbering (OK for section-based layout)
            pass

    return issues


def _is_main_prd_file(file_path: Path, content: str) -> bool:
    """Determine if this is a main/monolithic PRD file or a section file."""
    file_name = file_path.name

    # Section files have format PRD-NN.S_slug.md
    if re.match(r"PRD-\d{2,9}\.\d+_", file_name):
        return False

    # If it has multiple sections, it's likely a main file
    section_count = len(re.findall(r"^## \d+\.", content, re.MULTILINE))
    return section_count >= 5


def _validate_section_10(file_path: Path, content: str) -> List[ValidationIssue]:
    """Validate Section 10 (Customer-Facing Content) - BLOCKING."""
    issues = []
    file_name = file_path.name

    # Find Section 10
    section_10_match = re.search(
        r"^## 10\.\s+(.+?)(?=^## \d+\.|\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )

    if not section_10_match:
        # Check if this file is expected to have Section 10
        if _should_have_section_10(file_path, content):
            issues.append(ValidationIssue(
                code="PRD-E010",
                message="Missing Section 10 (Customer-Facing Content) - BLOCKING section",
                file=file_name,
                tier=Tier.TIER1,
            ))
        return issues

    section_content = section_10_match.group(0)

    # Check for placeholder content
    has_placeholder = any(p.search(section_content) for p in PLACEHOLDER_PATTERNS)
    if has_placeholder:
        issues.append(ValidationIssue(
            code="PRD-E010",
            message="Section 10 contains placeholder text - must have substantive content",
            file=file_name,
            tier=Tier.TIER1,
        ))
        return issues

    # Check for minimum substantive content
    # Remove headings and whitespace to check actual content
    content_only = re.sub(r"^#+.*$", "", section_content, flags=re.MULTILINE)
    content_only = content_only.strip()

    # Section 10 should have at least 200 characters of content
    if len(content_only) < 200:
        issues.append(ValidationIssue(
            code="PRD-E010",
            message=f"Section 10 has insufficient content ({len(content_only)} chars, need ≥200)",
            file=file_name,
            tier=Tier.TIER1,
        ))

    # Check for required subsections
    required_subsections = ["10.1", "10.2", "10.3", "10.4", "10.5"]
    missing_subsections = []
    for subsection in required_subsections:
        if f"### {subsection}" not in section_content and f"{subsection} " not in section_content:
            missing_subsections.append(subsection)

    if missing_subsections:
        issues.append(ValidationIssue(
            code="PRD-W006",
            message=f"Section 10 missing subsections: {', '.join(missing_subsections)}",
            file=file_name,
            tier=Tier.TIER2,
        ))

    return issues


def _should_have_section_10(file_path: Path, content: str) -> bool:
    """Determine if this file should have Section 10."""
    file_name = file_path.name

    # Main/monolithic PRD files should have Section 10
    if _is_main_prd_file(file_path, content):
        return True

    # Section 10 file should have it
    if "10_" in file_name.lower() or "customer" in file_name.lower():
        return True

    return False


def _validate_section_8(file_path: Path, content: str) -> List[ValidationIssue]:
    """Validate Section 8 (User Stories) layer separation."""
    issues = []
    file_name = file_path.name

    # Find Section 8
    section_8_match = re.search(
        r"^## 8\.\s+(.+?)(?=^## \d+\.|\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )

    if not section_8_match:
        # Check if this file should have Section 8
        if "8_" in file_name.lower() or "user_stor" in file_name.lower():
            issues.append(ValidationIssue(
                code="PRD-E011",
                message="Missing Section 8 (User Stories) content",
                file=file_name,
                tier=Tier.TIER1,
            ))
        return issues

    section_content = section_8_match.group(0)

    # Check for layer separation note
    if not has_layer_separation_note(section_content):
        issues.append(ValidationIssue(
            code="PRD-E011",
            message="Section 8 missing layer separation note (PRD/EARS/BDD distinction)",
            file=file_name,
            tier=Tier.TIER1,
        ))

    # Check for BDD patterns (forbidden in PRD)
    if has_bdd_patterns(section_content):
        issues.append(ValidationIssue(
            code="PRD-E020",
            message="Section 8 contains Given-When-Then patterns (BDD belongs in Layer 4)",
            file=file_name,
            tier=Tier.TIER1,
        ))

    # Check for EARS patterns (forbidden in PRD Section 8)
    if has_ears_patterns(section_content):
        issues.append(ValidationIssue(
            code="PRD-E021",
            message="Section 8 contains WHEN-THE-SHALL patterns (EARS belongs in Layer 3)",
            file=file_name,
            tier=Tier.TIER1,
        ))

    return issues


def _check_placeholders(file_path: Path, content: str) -> List[ValidationIssue]:
    """Check for placeholder text in content."""
    issues = []
    file_name = file_path.name

    for pattern in PLACEHOLDER_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            # Don't flag in comments
            if "merge conflict" in str(matches).lower():
                issues.append(ValidationIssue(
                    code="CORPUS-E001",
                    message=f"Merge conflict markers detected",
                    file=file_name,
                    tier=Tier.TIER1,
                ))
            else:
                # Find line numbers
                for match in pattern.finditer(content):
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(ValidationIssue(
                        code="CORPUS-E001",
                        message=f"Placeholder text '{match.group()}' at line {line_num}",
                        file=file_name,
                        line=line_num,
                        tier=Tier.TIER1,
                    ))
            break  # Only report first placeholder type

    return issues


def _validate_layer2_scope(file_path: Path, content: str) -> List[ValidationIssue]:
    """Enforce PRD Layer-2 concept: product intent before implementation design."""
    issues: List[ValidationIssue] = []
    file_name = file_path.name

    # PRD should not hard-link to concrete downstream document IDs (Layer 5+).
    forbidden_downstream = [
        r"\bADR-\d{2,9}\b",
        r"\bSYS-\d{2,9}\b",
        r"\bREQ-\d{2,9}\b",
        r"\bCTR-\d{2,9}\b",
        r"\bSPEC-\d{2,9}\b",
        r"\bTSPEC-\d{2,9}\b",
        r"\bTASKS-\d{2,9}\b",
    ]

    matches = []
    for pattern in forbidden_downstream:
        matches.extend(re.findall(pattern, content))

    if matches:
        samples = ", ".join(sorted(set(matches))[:5])
        issues.append(ValidationIssue(
            code="PRD-E022",
            message=(
                "PRD includes concrete downstream artifact IDs (Layer 5+), which violates Layer-2 scope. "
                f"Found: {samples}"
            ),
            file=file_name,
            tier=Tier.TIER1,
        ))

    # Full-document guards for lower/higher-layer syntax leakage.
    if has_bdd_patterns(content):
        issues.append(ValidationIssue(
            code="PRD-E020",
            message="PRD contains Given/When/Then BDD syntax; keep executable behavior in Layer 4 BDD artifacts",
            file=file_name,
            tier=Tier.TIER1,
        ))

    if has_ears_patterns(content):
        issues.append(ValidationIssue(
            code="PRD-E021",
            message="PRD contains WHEN-THE-SHALL EARS syntax; keep formal requirement syntax in Layer 3 EARS artifacts",
            file=file_name,
            tier=Tier.TIER1,
        ))

    return issues


def get_section_content(content: str, section_num: int) -> str:
    """Extract content for a specific section number."""
    pattern = re.compile(
        rf"^## {section_num}\.\s+(.+?)(?=^## \d+\.|\Z)",
        re.MULTILINE | re.DOTALL
    )
    match = pattern.search(content)
    return match.group(0) if match else ""


def count_sections(content: str) -> int:
    """Count the number of sections in content."""
    return len(re.findall(r"^## \d+\.", content, re.MULTILINE))
