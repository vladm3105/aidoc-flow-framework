#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated as of UCX v1.9.0.

Migration: Use `ucx validate brd <path>` instead (includes legacy detection).
Removal: This script will be removed in UCX v2.0.0.

See: /opt/data/docs_flow_framework/UCX/docs/QUICK_START.md

--- Original docstring below ---

Detect legacy element ID patterns in BRD documents.

This script complements validate_standardized_element_codes.py by detecting
legacy patterns that should be converted to the unified BRD.NN.TT.SS format.

Detects:
- Simple legacy: FR-001, AC-01, BC-02, etc.
- Compound legacy: FR-AI-001, FR-SEC-007, ADR-GOV-001, etc.
- Domain-prefixed: NFR-PERF-01, QA-TEST-001, etc.

Exit codes:
- 0: No legacy patterns found
- 2: Legacy patterns detected (blocking)
"""

import warnings

warnings.warn(
    "This script is deprecated. Use 'ucx validate brd <path>' instead. "
    "Will be removed in UCX v2.0.0.",
    DeprecationWarning,
    stacklevel=2
)

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple

# Legacy pattern regex - captures compound patterns like FR-AI-001, ADR-GOV-001
LEGACY_PATTERNS = [
    # Compound FR patterns: FR-DOMAIN-NNN (e.g., FR-AI-001, FR-SEC-007)
    (re.compile(r"\b(FR)-([A-Z]+)-(\d+)\b"), "Functional Requirement", "01"),
    # Compound ADR patterns: ADR-DOMAIN-NNN (e.g., ADR-GOV-001)
    (re.compile(r"\b(ADR)-([A-Z]+)-(\d+)\b"), "Architecture Topic", "32"),
    # Compound NFR patterns: NFR-DOMAIN-NNN
    (re.compile(r"\b(NFR)-([A-Z]+)-(\d+)\b"), "Quality Attribute", "02"),
    # Simple patterns: TYPE-NNN (e.g., AC-01, BC-02)
    (re.compile(r"\b(AC)-(\d+)\b"), "Acceptance Criteria", "06"),
    (re.compile(r"\b(BC)-(\d+)\b"), "Constraint", "03"),
    (re.compile(r"\b(BA)-(\d+)\b"), "Assumption", "04"),
    (re.compile(r"\b(BO)-(\d+)\b"), "Business Objective", "23"),
    (re.compile(r"\b(QA)-(\d+)\b"), "Quality Attribute", "02"),
    (re.compile(r"\b(TC)-(\d+)\b"), "Constraint", "03"),
    # Simple R-NN pattern (Risk)
    (re.compile(r"\b(R)-(\d+)\b"), "Risk", "05"),
    # Simple A-NN pattern (Assumption) - but avoid matching in URLs
    (re.compile(r"(?<![/.])\b(A)-(\d+)\b(?![/])"), "Assumption", "04"),
    # Simple C-NN pattern (Constraint)
    (re.compile(r"(?<![/.])\b(C)-(\d+)\b(?![/])"), "Constraint", "03"),
]

# Patterns to exclude (false positives)
EXCLUDE_PATTERNS = [
    re.compile(r"rg\s+-[AC]"),  # ripgrep flags
    re.compile(r"grep\s+-[AC]"),  # grep flags
    re.compile(r"-[AC]\s+\d+"),  # CLI flags with numbers
    re.compile(r"sha256:[a-f0-9]+"),  # SHA hashes
    re.compile(r"v\d+\.\d+"),  # Version strings
]


@dataclass
class LegacyMatch:
    """Represents a detected legacy pattern."""
    pattern: str
    element_type: str
    target_code: str
    file_path: Path
    line_num: int
    line_content: str

    def suggested_id(self, doc_num: str, seq: int) -> str:
        """Generate suggested compliant ID."""
        return f"BRD.{doc_num}.{self.target_code}.{seq:02d}"

    def to_output(self) -> str:
        return (
            f"[LEGACY] {self.file_path}:{self.line_num} "
            f"'{self.pattern}' -> should be BRD.NN.{self.target_code}.SS "
            f"({self.element_type})"
        )


def extract_doc_num(file_path: Path) -> str:
    """Extract document number from BRD filename."""
    match = re.search(r"BRD-(\d+)", file_path.name)
    if match:
        return match.group(1).zfill(2)
    return "XX"


def is_excluded(line: str) -> bool:
    """Check if line should be excluded from detection."""
    for pattern in EXCLUDE_PATTERNS:
        if pattern.search(line):
            return True
    return False


def is_in_code_block(lines: List[str], line_idx: int) -> bool:
    """Check if line is inside a code block."""
    in_block = False
    for i in range(line_idx):
        if lines[i].strip().startswith("```"):
            in_block = not in_block
    return in_block


def detect_legacy_patterns(file_path: Path) -> List[LegacyMatch]:
    """Detect all legacy patterns in a file."""
    matches: List[LegacyMatch] = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[WARN] Could not read {file_path}: {e}", file=sys.stderr)
        return matches

    lines = content.splitlines()

    for line_idx, line in enumerate(lines):
        line_num = line_idx + 1

        # Skip code blocks
        if is_in_code_block(lines, line_idx):
            continue

        # Skip excluded patterns
        if is_excluded(line):
            continue

        # Skip comment lines in tables that explain the format
        if "should be" in line.lower() or "example" in line.lower():
            continue

        for pattern, element_type, target_code in LEGACY_PATTERNS:
            for match in pattern.finditer(line):
                legacy_id = match.group(0)

                # Skip if this looks like a table header or example
                if f"| {legacy_id} |" in line and "Example" in line:
                    continue

                matches.append(LegacyMatch(
                    pattern=legacy_id,
                    element_type=element_type,
                    target_code=target_code,
                    file_path=file_path,
                    line_num=line_num,
                    line_content=line.strip()[:80],
                ))

    return matches


def is_target_brd_file(file_path: Path, root: Path) -> bool:
    """Check if file is a target BRD file for validation."""
    rel = file_path.relative_to(root)
    rel_str = str(rel)

    # Skip backup directories
    if "/.backup_" in rel_str or rel_str.startswith(".backup_"):
        return False
    # Skip examples
    if rel_str.startswith("examples/"):
        return False
    # Skip index files
    if file_path.name.startswith("BRD-00"):
        return False
    # Skip review/validation/fix reports
    if any(x in file_path.name for x in [".R_", ".V_", ".F_", ".A_"]):
        return False

    # Match BRD document patterns
    return bool(
        re.match(r"^BRD-\d+_[a-z0-9_]+\.md$", file_path.name)
        or re.match(r"^BRD-\d+\.\d+_[a-z0-9_]+\.md$", file_path.name)
    )


def resolve_scan_root(path_arg: Path) -> Path:
    """Resolve the BRD scan root directory."""
    if path_arg.name == "01_BRD" and path_arg.exists():
        return path_arg

    candidate = path_arg / "01_BRD"
    if candidate.exists():
        return candidate

    nested = path_arg / "docs" / "01_BRD"
    if nested.exists():
        return nested

    return path_arg


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect legacy element ID patterns in BRD documents."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="docs/01_BRD",
        help="Root path to scan for BRD documents.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed output including line content.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary statistics by pattern type.",
    )
    parser.add_argument(
        "--fix-preview",
        action="store_true",
        help="Show suggested ID conversions.",
    )
    args = parser.parse_args()

    root = resolve_scan_root(Path(args.path))
    if not root.exists():
        print(f"[ERROR] Scan path not found: {root}")
        return 2

    # Find target files
    target_files = [
        path
        for path in root.rglob("*.md")
        if is_target_brd_file(path, root)
    ]

    print(f"[INFO] Scanning {len(target_files)} BRD files under {root}")

    # Collect all matches
    all_matches: List[LegacyMatch] = []
    files_with_issues: Dict[Path, List[LegacyMatch]] = {}

    for file_path in sorted(target_files):
        matches = detect_legacy_patterns(file_path)
        if matches:
            all_matches.extend(matches)
            files_with_issues[file_path] = matches

    if not all_matches:
        print("[PASS] No legacy element ID patterns detected.")
        return 0

    # Print results
    print(f"\n[ERROR] Found {len(all_matches)} legacy patterns in {len(files_with_issues)} files:\n")

    for file_path, matches in sorted(files_with_issues.items()):
        print(f"  {file_path.relative_to(root)} ({len(matches)} patterns)")
        if args.verbose:
            for match in matches:
                print(f"    Line {match.line_num}: {match.pattern} -> BRD.NN.{match.target_code}.SS ({match.element_type})")

    if args.summary:
        print("\n[SUMMARY] Patterns by type:")
        type_counts: Dict[str, int] = {}
        for match in all_matches:
            key = f"{match.pattern.split('-')[0]}-* ({match.element_type})"
            type_counts[key] = type_counts.get(key, 0) + 1
        for pattern_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  {pattern_type}: {count}")

    if args.fix_preview:
        print("\n[FIX PREVIEW] Suggested conversions:")
        for file_path, matches in sorted(files_with_issues.items()):
            doc_num = extract_doc_num(file_path)
            print(f"\n  {file_path.name}:")
            # Group by target code and assign sequential numbers
            by_code: Dict[str, List[LegacyMatch]] = {}
            for match in matches:
                by_code.setdefault(match.target_code, []).append(match)
            for code, code_matches in sorted(by_code.items()):
                for seq, match in enumerate(code_matches, 1):
                    suggested = match.suggested_id(doc_num, seq)
                    print(f"    {match.pattern} -> {suggested}")

    print(f"\n[ERROR] LEGACY-E001: {len(all_matches)} legacy patterns must be converted to BRD.NN.TT.SS format.")
    print("  Reference: ID_NAMING_STANDARDS.md")

    return 2


if __name__ == "__main__":
    sys.exit(main())
