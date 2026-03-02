#!/usr/bin/env python3
"""Validate PRD element type codes against standardized naming contracts.

Checks:
- PRD element IDs follow PRD.NN.TT.SS pattern when present
- Element type code TT is valid for PRD artifacts
- Section-element semantic mapping is enforced for key PRD sections

Exit codes:
- 0: pass
- 2: validation errors present
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

ELEMENT_ID_PATTERN = re.compile(r"\bPRD\.(\d{2,})\.(\d{2})\.(\d{2,})\b")
SECTION_PATTERN = re.compile(r"^#{2,3}\s+(\d+(?:\.\d+)*)\.")

VALID_PRD_CODES = {
    "01",  # Functional Requirement
    "02",  # Quality Attribute
    "03",  # Constraint
    "04",  # Assumption
    "05",  # Dependency
    "06",  # Acceptance Criteria
    "07",  # Risk
    "08",  # Metric/KPI
    "09",  # User Story
    "10",  # Decision
    "22",  # Feature Item
    "24",  # Stakeholder Need
    "32",  # Architecture Topic
}

LEGACY_PRD_CODES = {
    "23": "Business Objective has BRD ownership; migrate to BRD.*.23.* references.",
}

# Section-to-element type code mapping for 21-section PRD-MVP-TEMPLATE
# Reference: ai_dev_ssd_flow/02_PRD/PRD-MVP-TEMPLATE.md
SECTION_CODE_MAP = {
    "5": "08",   # Section 5: Success Metrics (KPIs) → Metric/KPI
    "8": "09",   # Section 8: User Stories & User Roles → User Story
    "9": "01",   # Section 9: Functional Requirements → Functional Requirement
    "11": "06",  # Section 11: Acceptance Criteria → Acceptance Criteria
    "12": "03",  # Section 12: Constraints & Assumptions → Constraint (03), Assumptions use simple numbers
    "13": "07",  # Section 13: Risk Assessment → Risk
}


@dataclass
class Issue:
    code: str
    message: str
    file_path: Path
    line: int

    def to_output(self) -> str:
        return f"[ERROR] {self.code}: {self.file_path}:{self.line} {self.message}"


class WarningIssue(Issue):
    def to_output(self) -> str:
        return f"[WARN] {self.code}: {self.file_path}:{self.line} {self.message}"


def resolve_scan_root(path_arg: Path) -> Path:
    if path_arg.name == "02_PRD" and path_arg.exists():
        return path_arg

    candidate = path_arg / "02_PRD"
    if candidate.exists():
        return candidate

    nested = path_arg / "ai_dev_ssd_flow" / "02_PRD"
    if nested.exists():
        return nested

    return path_arg


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

            if element_type_code in LEGACY_PRD_CODES:
                warnings.append(
                    WarningIssue(
                        code="PRD-W023",
                        message=(
                            f"Element type code '{element_type_code}' is legacy in PRD. "
                            f"{LEGACY_PRD_CODES[element_type_code]}"
                        ),
                        file_path=file_path,
                        line=line_no,
                    )
                )
                continue

            if element_type_code not in VALID_PRD_CODES:
                issues.append(
                    Issue(
                        code="PRD-E020",
                        message=(
                            f"Element type code '{element_type_code}' is not valid for PRD "
                            "(see ID_NAMING_STANDARDS.md)."
                        ),
                        file_path=file_path,
                        line=line_no,
                    )
                )
                continue

            section_key = find_section_key(current_section)
            if section_key and section_key in SECTION_CODE_MAP:
                expected_code = SECTION_CODE_MAP[section_key]
                if element_type_code != expected_code:
                    issues.append(
                        Issue(
                            code="PRD-E022",
                            message=(
                                f"Section '{section_key}' typically requires element type code "
                                f"'{expected_code}', found '{element_type_code}'."
                            ),
                            file_path=file_path,
                            line=line_no,
                        )
                    )

    return issues, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate standardized PRD element type code usage."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="ai_dev_ssd_flow/02_PRD",
        help="Root path to scan (repo root, ai_dev_ssd_flow root, or 02_PRD path).",
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
        print(f"[ERROR] PRD-E001: Scan path not found: {root}")
        return 2

    target_files = [
        path
        for path in root.rglob("*.md")
        if is_target_prd_file(path, root)
    ]

    if args.verbose:
        print(f"[INFO] Scanning {len(target_files)} PRD files under {root}")

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
        print(f"[ERROR] PRD-E022: Found {len(all_issues)} standardized element code violations.")
        return 2

    print("[PASS] Standardized PRD element type code validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
