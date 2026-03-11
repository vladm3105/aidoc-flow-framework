"""BRD quality gate validation.

Implements 10 GATE checks:
- GATE-01: Placeholder text detection (Tier 1)
- GATE-02: Premature downstream references (Tier 1)
- GATE-03: Internal count consistency (Tier 2)
- GATE-04: Index synchronization (Tier 1)
- GATE-05: DEPRECATED (Inter-BRD cross-linking)
- GATE-06: Diagram contract validation (Tier 2, advisory)
- GATE-07: Glossary consistency (Tier 2)
- GATE-08: Element ID uniqueness (Tier 1 for duplicates, Tier 2 for misplaced)
- GATE-09: Cost estimate format (Tier 2)
- GATE-10: File size compliance (Tier 1 for >20K tokens)
"""

import re
from pathlib import Path
from typing import List, Optional, Set

from ucx.validators.common.result import (
    UnifiedValidationResult,
    ValidationTier,
)
from ucx.validators.common.frontmatter import FrontmatterResult
from ucx.validators.common.file_utils import count_tokens_estimate
from ucx.validators.brd.schema import (
    PLACEHOLDER_PATTERNS,
    DOWNSTREAM_REF_PATTERNS,
    DIAGRAM_TAG_PATTERNS,
    DIAGRAM_INTENT_FIELDS,
    MAX_TOKENS,
    QUALITY_GATE_TIERS,
)


def validate_quality_gates(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
    tier1_only: bool = False,
    frontmatter: Optional[FrontmatterResult] = None,
) -> None:
    """
    Run quality gate checks.

    Args:
        content: File content
        file_path: Path to file
        result: Result to populate
        tier1_only: If True, skip Tier 2 checks
        frontmatter: Parsed frontmatter (optional)
    """
    # GATE-01: Placeholder detection (Tier 1 for existing BRDs)
    _check_gate01_placeholders(content, file_path, result)

    # GATE-02: Premature downstream references (Tier 1)
    _check_gate02_downstream_refs(content, file_path, result)

    # GATE-04: Index synchronization (Tier 1) - requires section layout
    # Skipped for now - complex check requires section file detection

    # GATE-08: Element ID uniqueness handled in element_codes.py

    # GATE-10: File size compliance (Tier 1)
    _check_gate10_file_size(content, file_path, result)

    # Tier 2 checks (skip if tier1_only)
    if not tier1_only:
        # GATE-06: Diagram contract validation (advisory warnings)
        _check_gate06_diagrams(content, file_path, result, frontmatter)
        # GATE-03: Count consistency (Tier 2)
        _check_gate03_counts(content, file_path, result)

        # GATE-07: Glossary consistency (Tier 2)
        _check_gate07_glossary(content, file_path, result)

        # GATE-09: Cost estimate format (Tier 2)
        _check_gate09_costs(content, file_path, result)


def _check_gate01_placeholders(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """GATE-01: Check for placeholder text."""
    placeholders_found: List[str] = []
    lines = content.splitlines()
    in_code_block = False

    for line_no, line in enumerate(lines, start=1):
        # Toggle code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip content inside code blocks
        if in_code_block:
            continue

        for pattern in PLACEHOLDER_PATTERNS:
            matches = pattern.findall(line)
            for match in matches:
                placeholders_found.append(f"Line {line_no}: {match}")

    if placeholders_found:
        # Count unique placeholders
        unique_count = len(set(placeholders_found))
        result.add_issue(
            "GATE-E001",
            file_path=file_path,
            context=f"Found {len(placeholders_found)} placeholder(s): {placeholders_found[:3]}...",
            tier=ValidationTier.TIER1,
        )
    else:
        result.add_pass(f"{file_path.name}: No placeholder text found")


def _check_gate02_downstream_refs(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """GATE-02: Check for premature downstream references."""
    downstream_refs: List[str] = []
    lines = content.splitlines()
    in_code_block = False

    for line_no, line in enumerate(lines, start=1):
        # Toggle code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        for pattern in DOWNSTREAM_REF_PATTERNS:
            matches = pattern.findall(line)
            for match in matches:
                downstream_refs.append(f"Line {line_no}: {match}")

    if downstream_refs:
        result.add_issue(
            "GATE-E002",
            file_path=file_path,
            context=f"Found {len(downstream_refs)} premature downstream ref(s)",
            tier=ValidationTier.TIER1,
        )


def _check_gate06_diagrams(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
    frontmatter: Optional[FrontmatterResult] = None,
) -> None:
    """GATE-06: Check diagram contract tags."""
    # Determine enforcement origin
    origin = "prd"  # default
    if frontmatter:
        custom_fields = frontmatter.data.get("custom_fields", {})
        origin = str(custom_fields.get("diagram_enforcement_origin", "prd"))
        if origin not in {"brd", "prd"}:
            origin = "prd"

    is_legacy_mode = origin == "brd"

    # Check for diagram tags
    has_c4 = bool(DIAGRAM_TAG_PATTERNS["c4-l1"].search(content))
    has_dfd = bool(DIAGRAM_TAG_PATTERNS["dfd-l0"].search(content))
    has_seq_tag = bool(DIAGRAM_TAG_PATTERNS["sequence"].search(content))
    has_sequence_block = "sequenceDiagram" in content

    # C4-L1 and DFD-L0 are advisory warnings
    if not has_c4:
        result.add_issue(
            "BRD-W011",
            file_path=file_path,
            context="Missing BRD advisory diagram tag: @diagram: c4-l1",
            tier=ValidationTier.TIER2,
        )

    if not has_dfd:
        result.add_issue(
            "BRD-W012",
            file_path=file_path,
            context="Missing BRD advisory diagram tag: @diagram: dfd-l0",
            tier=ValidationTier.TIER2,
        )

    # Sequence diagram validation
    if is_legacy_mode:
        if not has_seq_tag:
            result.add_issue(
                "BRD-W013",
                file_path=file_path,
                context="Missing BRD legacy sequence tag",
                tier=ValidationTier.TIER2,
            )
    else:
        if has_sequence_block and not has_seq_tag:
            result.add_issue(
                "BRD-W013",
                file_path=file_path,
                context="Sequence diagram present without sequence tag",
                tier=ValidationTier.TIER2,
            )

    # Check diagram intent header fields
    should_check_intent = is_legacy_mode or has_c4 or has_dfd or has_seq_tag or has_sequence_block
    if should_check_intent:
        missing_fields = [f for f in DIAGRAM_INTENT_FIELDS if f not in content]
        if missing_fields:
            result.add_issue(
                "BRD-W014",
                file_path=file_path,
                context=f"Diagram intent header missing: {', '.join(missing_fields)}",
                tier=ValidationTier.TIER2,
            )


def _check_gate10_file_size(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """GATE-10: Check file size compliance."""
    estimated_tokens = count_tokens_estimate(content)

    if estimated_tokens > MAX_TOKENS:
        result.add_issue(
            "GATE-E010",
            file_path=file_path,
            context=f"File exceeds {MAX_TOKENS} tokens (estimated: {estimated_tokens})",
            tier=ValidationTier.TIER1,
        )
    else:
        result.metadata.setdefault("token_counts", {})[str(file_path)] = estimated_tokens


def _check_gate03_counts(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """GATE-03: Check internal count consistency."""
    # Look for stated counts like "5 requirements" and verify against actual items
    count_patterns = [
        (r"(\d+)\s+(?:functional\s+)?requirements?", r"BRD\.\d+\.01\.\d+"),
        (r"(\d+)\s+user\s+stor(?:y|ies)", r"BRD\.\d+\.09\.\d+"),
        (r"(\d+)\s+(?:quality\s+)?attributes?", r"BRD\.\d+\.02\.\d+"),
    ]

    for stated_pattern, element_pattern in count_patterns:
        stated_match = re.search(stated_pattern, content, re.IGNORECASE)
        if stated_match:
            stated_count = int(stated_match.group(1))
            actual_count = len(re.findall(element_pattern, content))

            if actual_count > 0 and stated_count != actual_count:
                result.add_issue(
                    "GATE-W003",
                    file_path=file_path,
                    context=f"Count mismatch: stated {stated_count}, found {actual_count}",
                    tier=ValidationTier.TIER2,
                )


def _check_gate07_glossary(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """GATE-07: Check glossary consistency."""
    # Extract glossary section
    glossary_match = re.search(
        r"## \d+\. Glossary.*?(?=## \d+\.|\Z)",
        content,
        re.DOTALL,
    )

    if not glossary_match:
        return  # No glossary section, skip check

    glossary = glossary_match.group(0)

    # Extract defined terms (typically bold or in table)
    defined_terms: Set[str] = set()

    # Table format: | **Term** | Definition |
    table_terms = re.findall(r"\|\s*\*\*([^*|]+)\*\*\s*\|", glossary)
    defined_terms.update(t.strip().lower() for t in table_terms)

    # Bold format: **Term**: Definition
    bold_terms = re.findall(r"\*\*([^*]+)\*\*:", glossary)
    defined_terms.update(t.strip().lower() for t in bold_terms)

    # Look for acronyms in content that should be in glossary
    acronyms = set(re.findall(r"\b([A-Z]{2,6})\b", content))
    common_acronyms = {"API", "UI", "UX", "MVP", "BRD", "PRD", "SLA", "SLO"}

    undefined_acronyms = []
    for acronym in acronyms:
        if acronym not in common_acronyms:
            if acronym.lower() not in defined_terms and acronym not in defined_terms:
                undefined_acronyms.append(acronym)

    if undefined_acronyms and len(undefined_acronyms) <= 10:
        result.add_issue(
            "GATE-W007",
            file_path=file_path,
            context=f"Undefined acronyms: {', '.join(sorted(undefined_acronyms)[:5])}",
            tier=ValidationTier.TIER2,
        )


def _check_gate09_costs(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """GATE-09: Check cost estimate format."""
    # Look for cost sections or tables
    cost_section_match = re.search(
        r"## \d+\. Cost.*?(?=## \d+\.|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )

    if not cost_section_match:
        return  # No cost section, skip check

    cost_section = cost_section_match.group(0)

    # Check for proper currency format ($X,XXX or $X.XM)
    has_currency = bool(re.search(r"\$[\d,]+(?:\.\d+)?[KMB]?", cost_section))

    # Check for vague estimates that should be quantified
    vague_estimates = re.findall(
        r"\b(low cost|high cost|minimal cost|significant cost|expensive)\b",
        cost_section,
        re.IGNORECASE,
    )

    if vague_estimates and not has_currency:
        result.add_issue(
            "GATE-W009",
            file_path=file_path,
            context=f"Vague cost estimates without currency values: {vague_estimates[:3]}",
            tier=ValidationTier.TIER2,
        )
