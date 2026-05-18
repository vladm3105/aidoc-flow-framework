#!/usr/bin/env python3
"""Detect legacy element ID patterns in PRD documents.

This script complements validate_prd_standardized_element_codes.py by detecting
legacy patterns that should be converted to the unified PRD.NN.TT.SS format.

Detects:
- Simple legacy: AC-01, BC-02, R-01, A-01, C-01
- Compound legacy: FR-AI-001, ADR-GOV-001, NFR-PERF-001
- PRD-specific legacy: UAC-01, AC-P1-01, AC-P2-03

Exit codes:
- 0: No legacy patterns found
- 2: Legacy patterns detected (blocking)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

LEGACY_PATTERNS = [
    (re.compile(r"\b(FR)-([A-Z]+)-(\d+)\b"), "Functional Requirement", "01"),
    (re.compile(r"\b(ADR)-([A-Z]+)-(\d+)\b"), "Architecture Topic", "32"),
    (re.compile(r"\b(NFR)-([A-Z]+)-(\d+)\b"), "Quality Attribute", "02"),
    (re.compile(r"\b(UAC)-(\d+)\b"), "Acceptance Criteria", "06"),
    (re.compile(r"\b(AC)-P\d+-(\d+)\b"), "Acceptance Criteria", "06"),
    (re.compile(r"\b(AC)-(\d+)\b"), "Acceptance Criteria", "06"),
    (re.compile(r"\b(BC)-(\d+)\b"), "Constraint", "03"),
    (re.compile(r"\b(BA)-(\d+)\b"), "Assumption", "04"),
    (re.compile(r"\b(BO)-(\d+)\b"), "Business Objective", "23"),
    (re.compile(r"\b(QA)-(\d+)\b"), "Quality Attribute", "02"),
    (re.compile(r"\b(TC)-(\d+)\b"), "Constraint", "03"),
    (re.compile(r"\b(R)-(\d+)\b"), "Risk", "07"),
    (re.compile(r"(?<![/.])\b(A)-(\d+)\b(?![/])"), "Assumption", "04"),
    (re.compile(r"(?<![/.])\b(C)-(\d+)\b(?![/])"), "Constraint", "03"),
]

EXCLUDE_PATTERNS = [
    re.compile(r"rg\s+-[AC]"),
    re.compile(r"grep\s+-[AC]"),
    re.compile(r"-[AC]\s+\d+"),
    re.compile(r"sha256:[a-f0-9]+"),
    re.compile(r"v\d+\.\d+"),
]


@dataclass
class LegacyMatch:
    pattern: str
    element_type: str
    target_code: str
    file_path: Path
    line_num: int
    line_content: str

    def suggested_id(self, doc_num: str, seq: int) -> str:
        return f"PRD.{doc_num}.{self.target_code}.{seq:02d}"

    def to_output(self) -> str:
        return (
            f"[LEGACY] {self.file_path}:{self.line_num} "
            f"'{self.pattern}' -> should be PRD.NN.{self.target_code}.SS "
            f"({self.element_type})"
        )


def extract_doc_num(file_path: Path) -> str:
    match = re.search(r"PRD-(\d+)", file_path.name)
    if match:
        return match.group(1).zfill(2)
    return "XX"


def is_excluded(line: str) -> bool:
    for pattern in EXCLUDE_PATTERNS:
        if pattern.search(line):
            return True
    return False


def is_in_code_block(lines: List[str], line_idx: int) -> bool:
    in_block = False
    for i in range(line_idx):
        if lines[i].strip().startswith("```"):
            in_block = not in_block
    return in_block


def detect_legacy_patterns(file_path: Path) -> List[LegacyMatch]:
    matches: List[LegacyMatch] = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"[WARN] Could not read {file_path}: {exc}", file=sys.stderr)
        return matches

    lines = content.splitlines()

    for line_idx, line in enumerate(lines):
        line_num = line_idx + 1

        if is_in_code_block(lines, line_idx):
            continue

        if is_excluded(line):
            continue

        if "should be" in line.lower() or "example" in line.lower():
            continue

        for pattern, element_type, target_code in LEGACY_PATTERNS:
            for match in pattern.finditer(line):
                legacy_id = match.group(0)

                if f"| {legacy_id} |" in line and "Example" in line:
                    continue

                matches.append(
                    LegacyMatch(
                        pattern=legacy_id,
                        element_type=element_type,
                        target_code=target_code,
                        file_path=file_path,
                        line_num=line_num,
                        line_content=line.strip()[:80],
                    )
                )

    return matches


def is_target_prd_file(file_path: Path, root: Path) -> bool:
    rel = file_path.relative_to(root)
    rel_str = str(rel)

    if "/.backup_" in rel_str or rel_str.startswith(".backup_"):
        return False
    if rel_str.startswith("examples/"):
        return False
    if file_path.name.startswith("PRD-00"):
        return False
    if any(x in file_path.name for x in [".R_", ".V_", ".F_", ".A_"]):
        return False

    return bool(
        re.match(r"^PRD-\d+_[a-z0-9_]+\.md$", file_path.name)
        or re.match(r"^PRD-\d+\.\d+_[a-z0-9_]+\.md$", file_path.name)
    )


def resolve_scan_root(path_arg: Path) -> Path:
    if path_arg.name == "02_PRD" and path_arg.exists():
        return path_arg

    candidate = path_arg / "02_PRD"
    if candidate.exists():
        return candidate

    nested = path_arg / "docs" / "02_PRD"
    if nested.exists():
        return nested

    flow_nested = path_arg / "ucx_flow_v3" / "02_PRD"
    if flow_nested.exists():
        return flow_nested

    return path_arg


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect legacy element ID patterns in PRD documents."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="ucx_flow_v3/02_PRD",
        help="Root path to scan for PRD documents.",
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
        print(f"[ERROR] Path not found: {root}", file=sys.stderr)
        return 2

    target_files = [
        file_path
        for file_path in sorted(root.rglob("*.md"))
        if is_target_prd_file(file_path, root)
    ]

    all_matches: List[LegacyMatch] = []
    for file_path in target_files:
        all_matches.extend(detect_legacy_patterns(file_path))

    if not all_matches:
        print("[PASS] No legacy PRD element ID patterns detected.")
        return 0

    pattern_counts: Dict[str, int] = {}
    for match in all_matches:
        pattern_counts[match.pattern] = pattern_counts.get(match.pattern, 0) + 1

    print(f"[ERROR] Found {len(all_matches)} legacy PRD element ID patterns in {len(target_files)} files")

    if args.summary:
        print("\nSummary by pattern:")
        for pattern, count in sorted(pattern_counts.items()):
            print(f"  - {pattern}: {count}")

    print("\nDetails:")
    for match in all_matches:
        print(match.to_output())
        if args.fix_preview:
            doc_num = extract_doc_num(match.file_path)
            print(f"         Suggested: {match.suggested_id(doc_num, 1)}")
            if args.verbose:
                print(f"         Context: {match.line_content}")

    return 2


if __name__ == "__main__":
    sys.exit(main())
