#!/usr/bin/env python3
"""
BDD Suite Validator (Section-Based Format)

Purpose: Enforce section-based file organization for BDD framework.
Section-based format is MANDATORY - no backward compatibility with legacy formats.

Valid Patterns (ONLY):
  1. Section-only: BDD-NN.SS_{slug}.feature (e.g., BDD-02.14_query_result_filtering.feature)
  2. Subsection: BDD-NN.SS.mm_{slug}.feature (e.g., BDD-02.24.01_quality_performance.feature)
  3. Aggregator: BDD-NN.SS.00_{slug}.feature (e.g., BDD-02.12.00_query_graph_traversal.feature)

Prohibited Patterns (ERROR):
  - _partN suffix (e.g., BDD-02_query_part1.feature)
  - Single-file format (e.g., BDD-02_knowledge_engine.feature)
  - Directory-based structure (e.g., BDD-02_{slug}/features/)

Checks (all blocking):
  - Section-based file naming (3 valid patterns only)
  - Prohibited pattern detection (legacy formats)
  - Aggregator requirements (@redirect tag, 0 scenarios)
  - Index file existence (BDD-NN.0_index.md)
  - Max 500 lines per .feature file; max 12 scenarios per Feature block
  - No Markdown headings inside .feature files
  - No ambiguous timezone abbreviations (EST/EDT/PST/…)
  - Threshold enforcement: @threshold:PRD.NN.* format
  - Section metadata tags (@section, @parent_doc, @index)

Usage:
  python ai_dev_flow/scripts/validate_bdd_suite.py --root docs/BDD --prd-root docs/PRD

Exit codes:
  0 = success, 1 = violations found
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple


# =============================================================================
# SECTION-BASED PATTERNS (Valid formats)
# =============================================================================

# Section-only format: BDD-NN.SS_{slug}.feature
SECTION_ONLY_PATTERN = re.compile(r"^BDD-\d{2,}\.\d+_[a-z0-9_]+\.feature$")

# Subsection format: BDD-NN.SS.mm_{slug}.feature
SUBSECTION_PATTERN = re.compile(r"^BDD-\d{2,}\.\d+\.\d{2}_[a-z0-9_]+\.feature$")

# Aggregator format: BDD-NN.SS.00_{slug}.feature (redirect stub)
AGGREGATOR_PATTERN = re.compile(r"^BDD-\d{2,}\.\d+\.00_[a-z0-9_]+\.feature$")

# Index file format: BDD-NN.0_index.md
INDEX_PATTERN = re.compile(r"^BDD-\d{2,}\.0_index\.md$")

# =============================================================================
# PROHIBITED PATTERNS (Legacy formats - cause ERROR)
# =============================================================================

# Prohibited: _partN suffix (e.g., BDD-02_query_part1.feature)
PART_SUFFIX_PATTERN = re.compile(r"^BDD-\d{2,}_[a-z0-9_]+_part\d+\.feature$", re.IGNORECASE)

# Prohibited: Single-file format (e.g., BDD-02_knowledge_engine.feature)
SINGLE_FILE_PATTERN = re.compile(r"^BDD-\d{2,}_[a-z0-9_]+\.feature$")

# =============================================================================
# GHERKIN PATTERNS
# =============================================================================

REDIRECT_TAG_RE = re.compile(r"^@.*\bredirect\b", re.IGNORECASE)
SCENARIO_RE = re.compile(r"^\s*Scenario(?: Outline)?:\s*", re.IGNORECASE)
FEATURE_RE = re.compile(r"^\s*Feature:\s*", re.IGNORECASE)
MD_HEADING_RE = re.compile(r"^\s*#{1,6}\s+")
AMBIG_TZ_RE = re.compile(r"\b(EST|EDT|PST|PDT|CST|CDT|IST|BST|GMT)\b")

# Section metadata tags
SECTION_TAG_RE = re.compile(r"^@section:\s*\d+\.\d+(?:\.\d+)?", re.IGNORECASE)
PARENT_DOC_TAG_RE = re.compile(r"^@parent_doc:\s*BDD-\d{2,}", re.IGNORECASE)
INDEX_TAG_RE = re.compile(r"^@index:\s*BDD-\d{2,}\.0_index\.md", re.IGNORECASE)

# Heuristics for raw durations/retries that should be expressed via @threshold
RAW_DURATION_RE = re.compile(
    r"\bWITHIN\s+\d+\s*(seconds?|minutes?)\b", re.IGNORECASE
)
RAW_RETRY_RE = re.compile(
    r"\b(after|within)\s+\d+\s*(attempts?|retries?)\b", re.IGNORECASE
)

THRESHOLD_TAG_RE = re.compile(
    r"@threshold\s*:\s*PRD\.(\d{2})\.[a-z0-9_]+(?:\.[a-z0-9_]+)*",
    re.IGNORECASE,
)


@dataclass
class Violation:
    path: Path
    line: int
    level: str  # ERROR | WARN
    message: str


def iter_feature_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.feature"):
        # Ignore archived materials
        if "archive" in p.parts:
            continue
        # Ignore template files
        if "-TEMPLATE" in p.name:
            continue
        yield p


def validate_section_based_file(path: Path, lines: List[str]) -> List[Violation]:
    """
    Validate section-based file naming and structure.
    
    Checks:
    1. Prohibited patterns (ERROR if found)
    2. Valid section pattern match (one of 3 patterns)
    3. Aggregator-specific validation (@redirect tag, 0 scenarios)
    4. Section metadata tags
    
    Returns list of violations.
    """
    violations: List[Violation] = []
    filename = path.name
    
    # Check prohibited patterns first (legacy formats)
    if PART_SUFFIX_PATTERN.match(filename):
        violations.append(
            Violation(
                path, 1, "ERROR",
                f"Prohibited _partN suffix detected. Use subsection format instead: "
                f"BDD-NN.SS.01_{{}}, BDD-NN.SS.02_{{}}, etc."
            )
        )
        return violations  # Don't continue if prohibited pattern found
    
    if SINGLE_FILE_PATTERN.match(filename) and not (SECTION_ONLY_PATTERN.match(filename) or SUBSECTION_PATTERN.match(filename) or AGGREGATOR_PATTERN.match(filename)):
        violations.append(
            Violation(
                path, 1, "ERROR",
                f"Prohibited single-file format detected. Use section-based format: "
                f"BDD-NN.SS_{{}}.feature"
            )
        )
        return violations
    
    # Validate section-based pattern (one of 3 valid patterns)
    is_section_only = SECTION_ONLY_PATTERN.match(filename)
    is_subsection = SUBSECTION_PATTERN.match(filename)
    is_aggregator = AGGREGATOR_PATTERN.match(filename)
    
    if not (is_section_only or is_subsection or is_aggregator):
        violations.append(
            Violation(
                path, 1, "ERROR",
                f"File does not match any valid section-based pattern. "
                f"Use: BDD-NN.SS_{{}}.feature, BDD-NN.SS.mm_{{}}.feature, or BDD-NN.SS.00_{{}}.feature"
            )
        )
        return violations
    
    # Aggregator-specific validation
    if is_aggregator:
        has_redirect_tag = any(REDIRECT_TAG_RE.search(l) for l in lines)
        has_scenarios = any(SCENARIO_RE.search(l) for l in lines)
        
        if not has_redirect_tag:
            violations.append(
                Violation(path, 1, "ERROR", "Aggregator file (.00) missing required @redirect tag")
            )
        
        if has_scenarios:
            # Find first offending line for context
            for i, l in enumerate(lines, 1):
                if SCENARIO_RE.search(l):
                    violations.append(
                        Violation(
                            path, i, "ERROR",
                            "Aggregator file (.00) must have 0 scenarios (redirect stub only)"
                        )
                    )
                    break
    
    # Validate section metadata tags (required for all .feature files)
    has_section_tag = any(SECTION_TAG_RE.search(l) for l in lines)
    has_parent_doc_tag = any(PARENT_DOC_TAG_RE.search(l) for l in lines)
    has_index_tag = any(INDEX_TAG_RE.search(l) for l in lines)
    
    if not has_section_tag:
        violations.append(
            Violation(path, 1, "ERROR", "Missing required @section: N.S metadata tag")
        )
    if not has_parent_doc_tag:
        violations.append(
            Violation(path, 1, "ERROR", "Missing required @parent_doc: BDD-NN metadata tag")
        )
    if not has_index_tag:
        violations.append(
            Violation(path, 1, "ERROR", "Missing required @index: BDD-NN.0_index.md metadata tag")
        )
    
    return violations


def check_size_and_counts(path: Path, lines: List[str]) -> List[Violation]:
    v: List[Violation] = []
    if len(lines) > 500:
        v.append(Violation(path, 1, "ERROR", f"File exceeds 500 lines ({len(lines)})"))

    # Count scenarios per Feature block
    feature_starts: List[int] = [i for i, l in enumerate(lines) if FEATURE_RE.search(l)]
    feature_starts.append(len(lines))  # sentinel to handle last block

    for idx in range(len(feature_starts) - 1):
        start = feature_starts[idx]
        end = feature_starts[idx + 1]
        block = lines[start:end]
        scenario_count = sum(1 for l in block if SCENARIO_RE.search(l))
        if scenario_count > 12:
            v.append(
                Violation(
                    path,
                    start + 1,
                    "ERROR",
                    f"Feature block has {scenario_count} scenarios (>12)",
                )
            )
    return v


def check_markdown_and_timezone(path: Path, lines: List[str]) -> List[Violation]:
    v: List[Violation] = []
    for i, l in enumerate(lines, 1):
        if MD_HEADING_RE.search(l):
            v.append(Violation(path, i, "ERROR", "Markdown headings not allowed in .feature"))
        if AMBIG_TZ_RE.search(l):
            v.append(
                Violation(
                    path,
                    i,
                    "ERROR",
                    "Ambiguous timezone abbreviation found (use IANA timezone, e.g., America/New_York)",
                )
            )
    return v


def check_thresholds(path: Path, lines: List[str], prd_root: Path) -> List[Violation]:
    v: List[Violation] = []
    content = "\n".join(lines)

    # Discourage raw durations / retries
    for m in RAW_DURATION_RE.finditer(content):
        # best-effort line number
        ln = content[: m.start()].count("\n") + 1
        v.append(
            Violation(
                path,
                ln,
                "ERROR",
                "Raw duration found; replace with @threshold:PRD.NN.timeout.<key>",
            )
        )
    for m in RAW_RETRY_RE.finditer(content):
        ln = content[: m.start()].count("\n") + 1
        v.append(
            Violation(
                path,
                ln,
                "ERROR",
                "Raw retry count found; replace with @threshold:PRD.NN.retry.<key>",
            )
        )

    # Verify threshold tag format and registry existence
    for m in THRESHOLD_TAG_RE.finditer(content):
        prd_num = m.group(1)  # zero-padded 2 digits
        # Registry file pattern: docs/PRD/PRD-XX_*/PRD-XX_threshold_registry.md
        candidates = list(prd_root.glob(f"PRD-{prd_num}_*/PRD-{prd_num}_threshold_registry.md"))
        if not candidates:
            ln = content[: m.start()].count("\n") + 1
            v.append(
                Violation(
                    path,
                    ln,
                    "ERROR",
                    f"Threshold registry for PRD-{prd_num} not found under docs/PRD",
                )
            )
    return v


def validate(root: Path, prd_root: Path) -> List[Violation]:
    """
    Validate section-based BDD suite structure.
    
    Requirements:
    - All .feature files at BDD/ root level (no subdirectories)
    - Index files (.0_index.md) exist for all BDD suites
    - All .feature files match section-based patterns
    - No legacy formats (single-file, directory-based)
    - No features/ subdirectory
    """
    violations: List[Violation] = []
    
    # Check for prohibited directory-based structure
    for subdir in root.iterdir():
        if subdir.is_dir() and subdir.name.startswith("BDD-"):
            # Check if it has features/ subdirectory (legacy structure)
            features_dir = subdir / "features"
            if features_dir.exists():
                violations.append(
                    Violation(
                        features_dir, 1, "ERROR",
                        f"Prohibited directory-based structure detected: {subdir.name}/features/. "
                        f"Migrate to section-based format at BDD/ root level."
                    )
                )
            # Any BDD-NN_{} directory is prohibited
            violations.append(
                Violation(
                    subdir, 1, "ERROR",
                    f"Prohibited directory structure: {subdir.name}/. "
                    f"All .feature files must be at BDD/ root level using section-based naming."
                )
            )
    
    # Collect all .feature files at BDD root (no recursion into subdirs)
    # Exclude template files
    feature_files = sorted([f for f in root.glob("*.feature") if "-TEMPLATE" not in f.name])
    
    # Validate index files (.0_index.md) exist for all BDD suites
    # Extract unique suite numbers from .feature files
    suite_numbers = set()
    for f in feature_files:
        # Extract BDD-NN from filename (e.g., BDD-02.14_query.feature → BDD-02)
        match = re.match(r"^BDD-(\d{2,})\.", f.name)
        if match:
            suite_numbers.add(match.group(1))
    
    # Check for index files
    for suite_num in sorted(suite_numbers):
        index_file = root / f"BDD-{suite_num}.0_index.md"
        if not index_file.exists():
            violations.append(
                Violation(
                    root, 1, "ERROR",
                    f"Missing required index file: BDD-{suite_num}.0_index.md"
                )
            )
    
    # Validate each .feature file
    for f in feature_files:
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            violations.append(Violation(f, 1, "ERROR", f"Failed to read file: {e}"))
            continue
        
        # Section-based validation (pattern, metadata, aggregator rules)
        violations.extend(validate_section_based_file(f, lines))
        
        # Size and scenario count limits
        violations.extend(check_size_and_counts(f, lines))
        
        # Markdown and timezone checks
        violations.extend(check_markdown_and_timezone(f, lines))
        
        # Threshold validation
        violations.extend(check_thresholds(f, lines, prd_root))
    
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate section-based BDD suites")
    parser.add_argument(
        "--root",
        default="docs/BDD",
        help="Root directory for BDD files (default: docs/BDD)",
    )
    parser.add_argument(
        "--prd-root",
        default="docs/PRD",
        help="Root directory for PRD threshold registries (default: docs/PRD)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    prd_root = Path(args.prd_root).resolve()

    v = validate(root, prd_root)
    if not v:
        print("✓ BDD validation passed (no violations)")
        return 0

    # Print grouped output
    errors = 0
    for item in v:
        prefix = "ERROR" if item.level.upper() == "ERROR" else "WARN"
        if item.level.upper() == "ERROR":
            errors += 1
        rel = item.path
        try:
            rel = item.path.relative_to(Path.cwd())
        except Exception:
            pass
        print(f"{prefix}: {rel}:{item.line}: {item.message}")

    print(f"\n❌ Validation failed: {errors} error(s), {len(v)-errors} warning(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
