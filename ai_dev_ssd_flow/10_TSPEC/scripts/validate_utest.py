#!/usr/bin/env python3
"""
UTEST Validator - Unit Test Specification Validation Script

Validates UTEST documents against MVP quality gates.
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationResult:
    """Validation result for a single document."""

    file_path: str
    passed: bool
    overall_score: float
    gate_scores: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


@dataclass
class TestCase:
    """Parsed test case from document."""

    id: str
    name: str
    category: Optional[str] = None
    req_ref: Optional[str] = None
    has_io_table: bool = False
    has_pseudocode: bool = False
    has_error_cases: bool = False


class UTESTValidator:
    """Validator for Unit Test Specification documents."""

    VALID_CATEGORIES = ["[Logic]", "[State]", "[Validation]", "[Edge]"]
    PASS_THRESHOLD = 90
    WARN_THRESHOLD = 80

    # Quality gate weights
    GATE_WEIGHTS = {
        "req_coverage": 0.30,
        "io_tables": 0.25,
        "category_prefixes": 0.15,
        "pseudocode": 0.15,
        "error_cases": 0.15,
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_cases: list[TestCase] = []
        self.req_refs: set[str] = set()
        self.spec_ref: Optional[str] = None

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single UTEST document."""
        if not file_path.exists():
            return ValidationResult(
                file_path=str(file_path),
                passed=False,
                overall_score=0,
                issues=[f"File not found: {file_path}"],
            )

        content = file_path.read_text(encoding="utf-8")
        self.test_cases = []
        self.req_refs = set()
        self.spec_ref = None

        # Parse document
        self._parse_document(content)

        # Calculate gate scores
        gate_scores = self._calculate_gate_scores()

        # Calculate overall score
        overall_score = sum(
            score * self.GATE_WEIGHTS[gate] for gate, score in gate_scores.items()
        )

        # Collect issues
        issues = self._collect_issues(gate_scores)
        warnings = self._collect_warnings(gate_scores)

        passed = overall_score >= self.PASS_THRESHOLD

        return ValidationResult(
            file_path=str(file_path),
            passed=passed,
            overall_score=overall_score,
            gate_scores=gate_scores,
            issues=issues,
            warnings=warnings,
        )

    def _parse_document(self, content: str) -> None:
        """Parse UTEST document content."""
        # Extract SPEC reference
        spec_match = re.search(r"@spec:\s*(SPEC-\d+)", content)
        if spec_match:
            self.spec_ref = spec_match.group(1)

        # Extract REQ references
        req_matches = re.findall(r"@req:\s*(REQ\.\d+\.\d+\.\d+)", content)
        self.req_refs = set(req_matches)

        # Extract test case index entries
        index_pattern = r"\|\s*(TSPEC\.\d+\.40\.\d+)\s*\|\s*([^|]+)\s*\|\s*(\[?\w+\]?)\s*\|"
        for match in re.finditer(index_pattern, content):
            test_id = match.group(1).strip()
            name = match.group(2).strip()
            category = match.group(3).strip()

            tc = TestCase(id=test_id, name=name, category=category)
            self.test_cases.append(tc)

        # Parse test case details
        self._parse_test_case_details(content)

    def _parse_test_case_details(self, content: str) -> None:
        """Parse detailed test case sections."""
        # Split by test case headers
        sections = re.split(r"###\s+TSPEC\.\d+\.40\.\d+:", content)

        for i, section in enumerate(sections[1:], 1):
            if i <= len(self.test_cases):
                tc = self.test_cases[i - 1]

                # Check for I/O table
                tc.has_io_table = bool(
                    re.search(r"\|\s*Input\s*\|\s*Expected Output", section)
                )

                # Check for pseudocode
                tc.has_pseudocode = bool(
                    re.search(r"GIVEN.*WHEN.*THEN", section, re.DOTALL)
                )

                # Check for error cases
                tc.has_error_cases = bool(
                    re.search(r"\|\s*Error Condition\s*\|\s*Expected Behavior", section)
                )

                # Extract REQ reference
                req_match = re.search(r"@req:\s*(REQ\.\d+\.\d+\.\d+)", section)
                if req_match:
                    tc.req_ref = req_match.group(1)

    def _calculate_gate_scores(self) -> dict:
        """Calculate quality gate scores."""
        total_tests = len(self.test_cases) or 1

        # GATE-01: REQ Coverage
        tests_with_req = sum(1 for tc in self.test_cases if tc.req_ref)
        req_coverage = (tests_with_req / total_tests) * 100

        # GATE-02: I/O Tables
        tests_with_io = sum(1 for tc in self.test_cases if tc.has_io_table)
        io_tables = (tests_with_io / total_tests) * 100

        # GATE-03: Category Prefixes
        tests_with_category = sum(
            1 for tc in self.test_cases if tc.category in self.VALID_CATEGORIES
        )
        category_prefixes = (tests_with_category / total_tests) * 100

        # GATE-04: Pseudocode
        tests_with_pseudo = sum(1 for tc in self.test_cases if tc.has_pseudocode)
        pseudocode = (tests_with_pseudo / total_tests) * 100

        # GATE-05: Error Cases
        tests_with_errors = sum(1 for tc in self.test_cases if tc.has_error_cases)
        error_cases = (tests_with_errors / total_tests) * 100

        return {
            "req_coverage": req_coverage,
            "io_tables": io_tables,
            "category_prefixes": category_prefixes,
            "pseudocode": pseudocode,
            "error_cases": error_cases,
        }

    def _collect_issues(self, gate_scores: dict) -> list:
        """Collect validation issues."""
        issues = []

        # Check for missing SPEC reference
        if not self.spec_ref:
            issues.append("Missing @spec reference in document")

        # Check for missing REQ references
        if not self.req_refs:
            issues.append("No @req references found in document")

        # Check individual test cases
        for tc in self.test_cases:
            if not tc.req_ref:
                issues.append(f"{tc.id}: Missing @req reference")
            if not tc.has_io_table:
                issues.append(f"{tc.id}: Missing I/O table")
            if tc.category not in self.VALID_CATEGORIES:
                issues.append(f"{tc.id}: Invalid or missing category prefix")

        # Check gate thresholds
        for gate, score in gate_scores.items():
            if score < self.WARN_THRESHOLD:
                issues.append(f"GATE {gate}: Score {score:.1f}% below threshold")

        return issues

    def _collect_warnings(self, gate_scores: dict) -> list:
        """Collect validation warnings."""
        warnings = []

        for tc in self.test_cases:
            if not tc.has_pseudocode:
                warnings.append(f"{tc.id}: Missing pseudocode (recommended)")
            if not tc.has_error_cases:
                warnings.append(f"{tc.id}: Missing error cases (recommended)")

        return warnings


def format_result(result: ValidationResult, verbose: bool = False) -> str:
    """Format validation result for output."""
    status = "✅ PASS" if result.passed else "❌ FAIL"
    if not result.passed and result.overall_score >= 80:
        status = "⚠️ WARN"

    output = [f"{status} {result.file_path}: {result.overall_score:.1f}%"]

    if verbose:
        output.append("\nQuality Gates:")
        gate_names = {
            "req_coverage": "GATE-01 REQ Coverage",
            "io_tables": "GATE-02 I/O Tables",
            "category_prefixes": "GATE-03 Category Prefix",
            "pseudocode": "GATE-04 Pseudocode",
            "error_cases": "GATE-05 Error Cases",
        }
        for gate, score in result.gate_scores.items():
            gate_status = "✅" if score >= 80 else "❌"
            output.append(f"  {gate_names[gate]}: {score:.1f}% {gate_status}")

        if result.issues:
            output.append("\nIssues:")
            for issue in result.issues[:10]:
                output.append(f"  - {issue}")
            if len(result.issues) > 10:
                output.append(f"  ... and {len(result.issues) - 10} more")

        if result.warnings and verbose:
            output.append("\nWarnings:")
            for warning in result.warnings[:5]:
                output.append(f"  - {warning}")

    return "\n".join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate UTEST (Unit Test Specification) documents"
    )
    parser.add_argument("files", nargs="+", type=Path, help="UTEST files to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--quality-gates", action="store_true", help="Show quality gate breakdown"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    validator = UTESTValidator(verbose=args.verbose or args.quality_gates)
    results = []
    all_passed = True

    for file_path in args.files:
        result = validator.validate_file(file_path)
        results.append(result)
        if not result.passed:
            all_passed = False

        print(format_result(result, args.verbose or args.quality_gates))
        print()

    # Summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"Summary: {passed}/{total} documents passed validation")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
