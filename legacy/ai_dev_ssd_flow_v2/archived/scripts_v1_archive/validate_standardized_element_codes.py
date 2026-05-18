#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated as of UCX v1.9.0.

Migration: Use `ucx validate brd <path>` instead.
Removal: This script will be removed in UCX v2.0.0.

See: /opt/data/docs_flow_framework/UCX/docs/QUICK_START.md

--- Original docstring below ---

Validate BRD element type codes against standardized naming contracts.

Checks:
- BRD element IDs follow BRD.NN.TT.SS pattern when present
- Element type code TT is valid for BRD artifacts
- Section-element semantic mapping is enforced for key BRD sections

Exit codes:
- 0: pass
- 2: validation errors present
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
from typing import Dict, List, Optional, Set, Union

ELEMENT_ID_PATTERN = re.compile(r"\bBRD\.(\d{2,})\.(\d{2})\.(\d{2,})\b")
SECTION_PATTERN = re.compile(r"^#{2,3}\s+(\d+(?:\.\d+)*)\.")

VALID_BRD_CODES = {
    "01",  # Functional Requirement
    "02",  # Quality Attribute (generic)
    "03",  # Constraint
    "04",  # Assumption
    "05",  # Dependency
    "06",  # Acceptance Criteria
    "07",  # Risk
    "08",  # Metric
    "09",  # User Story
    "10",  # Decision
    "22",  # Feature Item
    "23",  # Business Objective
    "24",  # Stakeholder Need
    "32",  # Architecture Topic (Legacy compatibility)
    # Quality Attribute Subcategories (91-99 series) - Section 7.x
    "91",  # Performance Requirement (Section 7.3)
    "92",  # Reliability Requirement (Section 7.4)
    "93",  # Availability Requirement (reserved)
    "94",  # Scalability Requirement (Section 7.5)
    "95",  # Usability Requirement (reserved)
    "96",  # Security Requirement (Section 7.6)
    "97",  # Compatibility Requirement (reserved)
    "98",  # Observability Requirement (Section 7.7)
    "99",  # Maintainability Requirement (Section 7.8)
}

# Maps section number to valid element type code(s)
# Values can be a single code string or a set of valid codes
# Source: ID_NAMING_STANDARDS.md - QA Subcategories use hierarchical codes 91-99
SECTION_CODE_MAP: Dict[str, Union[str, Set[str]]] = {
    "2": "23",           # Business Objectives
    "3": "22",           # Project Scope / Feature Items
    "4": "24",           # Stakeholders / Stakeholder Needs
    "5": "09",           # User Stories
    "6": {"01", "06"},   # Functional Requirements (01) + embedded Acceptance Criteria tables (06)
    "7.1": "02",         # Quality Attributes (generic overview)
    "7.2": {"10", "32"},  # ADR Topics / Architecture Topics (10 canonical, 32 legacy)
    # Quality Attribute Subcategory Sections - hierarchical codes 91-99
    # Code 02/05 tolerated for legacy; specific 9x codes are canonical
    "7.3": {"02", "05", "91"},  # Performance Requirements (91 canonical)
    "7.4": {"02", "05", "92"},  # Reliability Requirements (92 canonical)
    "7.5": {"02", "05", "94"},  # Scalability Requirements (94 canonical)
    "7.6": {"02", "05", "96"},  # Security Requirements (96 canonical)
    "7.7": {"02", "05", "98"},  # Observability Requirements (98 canonical)
    "7.8": {"02", "05", "99"},  # Maintainability Requirements (99 canonical)
    "8.1": "03",         # Constraints
    "8.2": "04",         # Assumptions
    "9": "06",           # Acceptance Criteria
    "10": {"05", "07"},  # Risk Management: 07 canonical, 05 tolerated for legacy docs
}

PREFERRED_SECTION_CODES: Dict[str, str] = {
    "6": "01",   # Functional Requirements primary; Acceptance Criteria embedded
    "7.2": "10", # Decision (canonical) over Architecture Topic (legacy)
    "7.3": "91", # Performance
    "7.4": "92", # Reliability
    "7.5": "94", # Scalability
    "7.6": "96", # Security
    "7.7": "98", # Observability
    "7.8": "99", # Maintainability
    "10": "07",  # Risk (canonical) over Dependency (legacy)
}


@dataclass
class Issue:
    code: str
    message: str
    file_path: Path
    line: int

    def to_output(self) -> str:
        return f"[ERROR] {self.code}: {self.file_path}:{self.line} {self.message}"


@dataclass
class WarningIssue:
    code: str
    message: str
    file_path: Path
    line: int

    def to_output(self) -> str:
        return f"[WARN] {self.code}: {self.file_path}:{self.line} {self.message}"


def resolve_scan_root(path_arg: Path) -> Path:
    if path_arg.name == "01_BRD" and path_arg.exists():
        return path_arg

    candidate = path_arg / "01_BRD"
    if candidate.exists():
        return candidate

    nested = path_arg / "ucx_flow_v3" / "01_BRD"
    if nested.exists():
        return nested

    return path_arg


def is_target_brd_file(file_path: Path, root: Path) -> bool:
    rel = file_path.relative_to(root)
    rel_str = str(rel)

    if "/.backup_" in rel_str or rel_str.startswith(".backup_"):
        return False
    if rel_str.startswith("examples/"):
        return False
    if file_path.name.startswith("BRD-00"):
        return False

    return bool(
        re.match(r"^BRD-\d+_[a-z0-9_]+\.md$", file_path.name)
        or re.match(r"^BRD-\d+\.\d+_[a-z0-9_]+\.md$", file_path.name)
    )


def find_section_key(current_section: Optional[str]) -> Optional[str]:
    if not current_section:
        return None

    if current_section in SECTION_CODE_MAP:
        return current_section

    first = current_section.split(".")[0]
    if first in SECTION_CODE_MAP:
        return first

    return None


def validate_file(file_path: Path) -> tuple[List[Issue], List[WarningIssue]]:
    issues: List[Issue] = []
    warnings: List[WarningIssue] = []
    current_section: Optional[str] = None
    in_code_block = False

    lines = file_path.read_text(encoding="utf-8").splitlines()

    for line_no, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        section_match = SECTION_PATTERN.match(line)
        if section_match:
            current_section = section_match.group(1)

        for match in ELEMENT_ID_PATTERN.finditer(line):
            element_type_code = match.group(2)

            if element_type_code not in VALID_BRD_CODES:
                issues.append(
                    Issue(
                        code="BRD-E020",
                        message=(
                            f"Element type code '{element_type_code}' is not valid for BRD "
                            "(see ID_NAMING_STANDARDS.md)."
                        ),
                        file_path=file_path,
                        line=line_no,
                    )
                )
                continue

            section_key = find_section_key(current_section)
            if section_key and section_key in SECTION_CODE_MAP:
                expected = SECTION_CODE_MAP[section_key]
                # Handle both single code (str) and multiple valid codes (set)
                valid_codes = expected if isinstance(expected, set) else {expected}
                if element_type_code not in valid_codes:
                    codes_str = " or ".join(f"'{c}'" for c in sorted(valid_codes))
                    issues.append(
                        Issue(
                            code="BRD-E022",
                            message=(
                                f"Section '{section_key}' requires element type code {codes_str}, "
                                f"found '{element_type_code}'."
                            ),
                            file_path=file_path,
                            line=line_no,
                        )
                    )

                preferred_code = PREFERRED_SECTION_CODES.get(section_key)
                if preferred_code and element_type_code in valid_codes and element_type_code != preferred_code:
                    warnings.append(
                        WarningIssue(
                            code="BRD-W023",
                            message=(
                                f"Section '{section_key}' prefers element type code '{preferred_code}'; "
                                f"found legacy-compatible '{element_type_code}'."
                            ),
                            file_path=file_path,
                            line=line_no,
                        )
                    )

    return issues, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate standardized BRD element type code usage."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="ucx_flow_v3/01_BRD",
        help="Root path to scan (repo root, ucx_flow_v3 root, or 01_BRD path).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Reserved for interface compatibility; validation errors are always blocking.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print scanned file count.",
    )
    args = parser.parse_args()

    root = resolve_scan_root(Path(args.path))
    if not root.exists():
        print(f"[ERROR] BRD-E001: Scan path not found: {root}")
        return 2

    target_files = [
        path
        for path in root.rglob("*.md")
        if is_target_brd_file(path, root)
    ]

    if args.verbose:
        print(f"[INFO] Scanning {len(target_files)} BRD files under {root}")

    all_issues: List[Issue] = []
    all_warnings: List[WarningIssue] = []
    for file_path in sorted(target_files):
        file_issues, file_warnings = validate_file(file_path)
        all_issues.extend(file_issues)
        all_warnings.extend(file_warnings)

    for warning in all_warnings:
        print(warning.to_output())

    if all_issues:
        for issue in all_issues:
            print(issue.to_output())
        print(f"[ERROR] BRD-E022: Found {len(all_issues)} standardized element code violations.")
        return 2

    print("[PASS] Standardized element type code validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
