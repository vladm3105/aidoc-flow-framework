"""PRD Corpus-Level Validation Module.

Validates cross-file consistency and completeness across PRD corpus:
- Element ID uniqueness across files
- Section coverage across section-based layout
- Cross-file reference consistency
- Naming convention alignment
- Combined content token limits
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Optional

from ucx.validators.prd import ValidationIssue, Tier
from ucx.validators.prd.schema import (
    REQUIRED_SECTIONS,
    TOKEN_WARNING,
    TOKEN_ERROR,
    estimate_tokens,
)


def run_corpus_checks(
    corpus_path: Path,
    files: List[Path],
    tier1_only: bool = False,
) -> List[ValidationIssue]:
    """Run corpus-level validation checks.

    Args:
        corpus_path: Path to PRD corpus directory
        files: List of PRD files in corpus
        tier1_only: Only run Tier 1 checks

    Returns:
        List of validation issues
    """
    issues = []

    if len(files) < 2:
        # Single file, skip corpus checks
        return issues

    # Read all file contents
    file_contents: Dict[Path, str] = {}
    for file_path in files:
        try:
            file_contents[file_path] = file_path.read_text(encoding='utf-8')
        except Exception:
            continue

    # Tier 1 (Blocking) Corpus Checks
    issues.extend(_check_corpus_element_uniqueness(file_contents))
    issues.extend(_check_corpus_token_limit(file_contents))

    # Tier 2 (Advisory) Corpus Checks - skip if tier1_only
    if not tier1_only:
        issues.extend(_check_section_coverage(corpus_path, file_contents))
        issues.extend(_check_naming_consistency(corpus_path, files))
        issues.extend(_check_cross_file_references(file_contents))
        issues.extend(_check_doc_id_consistency(file_contents))

    return issues


def _check_corpus_element_uniqueness(
    file_contents: Dict[Path, str],
) -> List[ValidationIssue]:
    """Check element ID uniqueness across all files."""
    issues = []

    # Track element definitions across files
    element_locations: Dict[str, List[tuple[str, int]]] = {}
    element_pattern = re.compile(r"\bPRD\.(\d{2})\.(\d{2})\.(\d{2})\b")

    for file_path, content in file_contents.items():
        file_name = file_path.name

        for match in element_pattern.finditer(content):
            element_id = match.group(0)
            line_num = content[:match.start()].count('\n') + 1

            # Check if definition context
            line_start = content.rfind('\n', 0, match.start()) + 1
            line_end_idx = content.find('\n', match.end())
            if line_end_idx == -1:
                line_end_idx = len(content)
            full_line = content[line_start:line_end_idx]
            prefix = content[line_start:match.start()].strip()

            # Skip reference lines — mirrors element_codes._is_definition_context()
            is_reference = (
                '\u2192' in full_line or
                '@brd:' in full_line.lower() or
                '@prd:' in full_line.lower() or
                'traces to' in full_line.lower() or
                'references ' in full_line.lower()
            )

            is_definition = not is_reference and (
                prefix == "" or
                prefix == "-" or
                prefix == "*" or
                prefix.endswith("|") or
                prefix.endswith("**")
            )

            if is_definition:
                if element_id not in element_locations:
                    element_locations[element_id] = []
                element_locations[element_id].append((file_name, line_num))

    # Report duplicates across files
    for element_id, locations in element_locations.items():
        if len(locations) > 1:
            # Check if definitions are in different files
            files_with_def = set(loc[0] for loc in locations)
            if len(files_with_def) > 1:
                loc_str = ", ".join(f"{f}:{l}" for f, l in locations[:3])
                issues.append(ValidationIssue(
                    code="CORPUS-E008",
                    message=f"Element {element_id} defined in multiple files: {loc_str}",
                    file="corpus",
                    tier=Tier.TIER1,
                ))

    return issues


def _check_corpus_token_limit(
    file_contents: Dict[Path, str],
) -> List[ValidationIssue]:
    """Check combined token count across corpus."""
    issues = []

    total_tokens = sum(estimate_tokens(content) for content in file_contents.values())

    if total_tokens > TOKEN_ERROR * 2:  # 160K tokens for corpus
        issues.append(ValidationIssue(
            code="CORPUS-E010",
            message=f"Corpus has ~{total_tokens} tokens, exceeds {TOKEN_ERROR * 2} combined limit",
            file="corpus",
            tier=Tier.TIER1,
        ))
    elif total_tokens > TOKEN_WARNING * 2:  # 80K tokens warning
        issues.append(ValidationIssue(
            code="CORPUS-W010",
            message=f"Corpus has ~{total_tokens} tokens, approaching {TOKEN_ERROR * 2} limit",
            file="corpus",
            tier=Tier.TIER2,
        ))

    return issues


def _check_section_coverage(
    corpus_path: Path,
    file_contents: Dict[Path, str],
) -> List[ValidationIssue]:
    """Check section coverage in section-based layout."""
    issues = []

    # Detect if using section-based layout
    section_file_pattern = re.compile(r"PRD-\d{2}\.(\d+)_")
    section_files = [f for f in file_contents.keys() if section_file_pattern.match(f.name)]

    if not section_files:
        # Not using section-based layout
        return issues

    # Map found sections from filenames
    found_sections: Set[int] = set()
    for file_path in section_files:
        match = section_file_pattern.match(file_path.name)
        if match:
            section_num = int(match.group(1))
            found_sections.add(section_num)

    # Also check for sections in combined content
    section_header_pattern = re.compile(r"^## (\d+)\.", re.MULTILINE)
    for content in file_contents.values():
        for match in section_header_pattern.finditer(content):
            found_sections.add(int(match.group(1)))

    # Check for missing sections
    missing = [s for s in REQUIRED_SECTIONS if s not in found_sections]

    if missing:
        issues.append(ValidationIssue(
            code="CORPUS-W004",
            message=f"Section-based layout missing sections: {missing}",
            file="corpus",
            tier=Tier.TIER2,
        ))

    return issues


def _check_naming_consistency(
    corpus_path: Path,
    files: List[Path],
) -> List[ValidationIssue]:
    """Check file naming consistency."""
    issues = []

    # Extract doc numbers from filenames
    doc_pattern = re.compile(r"PRD-(\d{2})")
    doc_numbers: Set[str] = set()

    for file_path in files:
        match = doc_pattern.search(file_path.name)
        if match:
            doc_numbers.add(match.group(1))

    # All files should use same doc number
    if len(doc_numbers) > 1:
        issues.append(ValidationIssue(
            code="CORPUS-W005",
            message=f"Mixed document numbers in corpus: {sorted(doc_numbers)}",
            file="corpus",
            tier=Tier.TIER2,
        ))

    # Check for consistent naming pattern
    has_section_files = any(re.match(r"PRD-\d{2}\.\d+_", f.name) for f in files)
    has_main_file = any(re.match(r"PRD-\d{2}_[a-z]", f.name) for f in files)

    if has_section_files and has_main_file:
        issues.append(ValidationIssue(
            code="CORPUS-W006",
            message="Mixed layout: both section files (PRD-NN.S_) and main file (PRD-NN_) found",
            file="corpus",
            tier=Tier.TIER2,
        ))

    return issues


def _check_cross_file_references(
    file_contents: Dict[Path, str],
) -> List[ValidationIssue]:
    """Check cross-file reference consistency."""
    issues = []

    # Collect all definitions and references
    all_definitions: Set[str] = set()
    all_references: Set[str] = set()

    element_pattern = re.compile(r"\bPRD\.(\d{2})\.(\d{2})\.(\d{2})\b")
    ref_pattern = re.compile(r"(?:see|ref|→)\s*(PRD\.\d{2}\.\d{2}\.\d{2})", re.IGNORECASE)

    for content in file_contents.values():
        # Get definitions
        for match in element_pattern.finditer(content):
            element_id = match.group(0)
            line_start = content.rfind('\n', 0, match.start()) + 1
            prefix = content[line_start:match.start()].strip()

            is_definition = (
                prefix == "" or
                prefix == "-" or
                prefix == "*" or
                prefix.endswith("|") or
                prefix.endswith("**")
            )

            if is_definition:
                all_definitions.add(element_id)

        # Get references
        for match in ref_pattern.finditer(content):
            all_references.add(match.group(1))

    # Find undefined references
    undefined = all_references - all_definitions
    if undefined:
        issues.append(ValidationIssue(
            code="CORPUS-W007",
            message=f"References to undefined elements: {list(undefined)[:5]}",
            file="corpus",
            tier=Tier.TIER2,
        ))

    return issues


def _check_doc_id_consistency(
    file_contents: Dict[Path, str],
) -> List[ValidationIssue]:
    """Check doc_id consistency in frontmatter across files."""
    issues = []

    doc_ids: Dict[str, str] = {}
    doc_id_pattern = re.compile(r"^doc_id:\s*['\"]?(PRD-\d{2})['\"]?\s*$", re.MULTILINE)

    for file_path, content in file_contents.items():
        match = doc_id_pattern.search(content)
        if match:
            doc_ids[file_path.name] = match.group(1)

    # Check consistency
    unique_ids = set(doc_ids.values())
    if len(unique_ids) > 1:
        issues.append(ValidationIssue(
            code="CORPUS-W009",
            message=f"Inconsistent doc_id values in frontmatter: {list(unique_ids)}",
            file="corpus",
            tier=Tier.TIER2,
        ))

    return issues


def get_corpus_statistics(files: List[Path]) -> Dict:
    """Calculate corpus statistics for reporting."""
    stats = {
        "file_count": len(files),
        "total_lines": 0,
        "total_tokens": 0,
        "element_count": 0,
        "section_coverage": 0,
        "files": [],
    }

    element_pattern = re.compile(r"\bPRD\.(\d{2})\.(\d{2})\.(\d{2})\b")
    found_sections: Set[int] = set()
    all_elements: Set[str] = set()

    for file_path in files:
        try:
            content = file_path.read_text(encoding='utf-8')
            # Keep line counting consistent with quality gates.
            lines = max(1, len(content.splitlines()))
            tokens = estimate_tokens(content)

            stats["total_lines"] += lines
            stats["total_tokens"] += tokens

            # Count elements
            for match in element_pattern.finditer(content):
                all_elements.add(match.group(0))

            # Track sections
            for match in re.finditer(r"^## (\d+)\.", content, re.MULTILINE):
                found_sections.add(int(match.group(1)))

            stats["files"].append({
                "name": file_path.name,
                "lines": lines,
                "tokens": tokens,
            })
        except Exception:
            continue

    stats["element_count"] = len(all_elements)
    stats["section_coverage"] = len(found_sections) / 21 * 100 if found_sections else 0

    return stats
