#!/usr/bin/env python3
"""
STEST Validator - Smoke Test Specification Validation Script

Validates STEST documents against MVP quality gates.
STEST requires 100% compliance - no partial passes.
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
    timeout: int = 0
    has_pass_fail: bool = False
    has_health_check: bool = False
    has_rollback: bool = False
    ears_ref: Optional[str] = None
    bdd_ref: Optional[str] = None


class STESTValidator:
    """Validator for Smoke Test Specification documents."""

    PASS_THRESHOLD = 100  # STEST requires 100%
    MAX_TOTAL_TIMEOUT = 300  # 5 minutes max
    MAX_TEST_TIMEOUT = 60  # 60 seconds per test

    GATE_WEIGHTS = {
        "critical_paths": 0.30,
        "timeout_budget": 0.25,
        "rollback_defined": 0.25,
        "health_checks": 0.20,
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_cases: list[TestCase] = []
        self.total_timeout: int = 0
        self.has_ears_tag: bool = False
        self.has_bdd_tag: bool = False
        self.has_req_tag: bool = False

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single STEST document."""
        if not file_path.exists():
            return ValidationResult(
                file_path=str(file_path),
                passed=False,
                overall_score=0,
                issues=[f"File not found: {file_path}"],
            )

        content = file_path.read_text(encoding="utf-8")
        self._reset_state()
        self._parse_document(content)

        gate_scores = self._calculate_gate_scores()
        overall_score = sum(
            score * self.GATE_WEIGHTS[gate] for gate, score in gate_scores.items()
        )

        issues = self._collect_issues(gate_scores)
        warnings = self._collect_warnings()

        # STEST requires 100%
        passed = overall_score >= self.PASS_THRESHOLD

        return ValidationResult(
            file_path=str(file_path),
            passed=passed,
            overall_score=overall_score,
            gate_scores=gate_scores,
            issues=issues,
            warnings=warnings,
        )

    def _reset_state(self) -> None:
        """Reset validator state."""
        self.test_cases = []
        self.total_timeout = 0
        self.has_ears_tag = False
        self.has_bdd_tag = False
        self.has_req_tag = False

    def _parse_document(self, content: str) -> None:
        """Parse STEST document content."""
        # Extract traceability tags
        if re.search(r"@ears:\s*EARS\.\d+\.\d+\.\d+", content):
            self.has_ears_tag = True
        if re.search(r"@bdd:\s*BDD\.\d+\.\d+\.\d+", content):
            self.has_bdd_tag = True
        if re.search(r"@req:\s*REQ\.\d+\.\d+\.\d+", content):
            self.has_req_tag = True

        # Extract total timeout budget
        timeout_match = re.search(
            r"\*\*Total Timeout Budget\*\*\s*\|\s*(\d+)", content
        )
        if timeout_match:
            self.total_timeout = int(timeout_match.group(1))

        # Extract test case index entries
        index_pattern = (
            r"\|\s*(TSPEC\.\d+\.42\.\d+)\s*\|\s*([^|]+)\s*\|\s*(\d+)s?\s*\|"
        )
        for match in re.finditer(index_pattern, content):
            test_id = match.group(1).strip()
            name = match.group(2).strip()
            timeout = int(match.group(3))

            tc = TestCase(id=test_id, name=name, timeout=timeout)
            self.test_cases.append(tc)

        self._parse_test_case_details(content)

    def _parse_test_case_details(self, content: str) -> None:
        """Parse detailed test case sections."""
        sections = re.split(r"###\s+TSPEC\.\d+\.42\.\d+:", content)

        for i, section in enumerate(sections[1:], 1):
            if i <= len(self.test_cases):
                tc = self.test_cases[i - 1]

                # Check for pass/fail criteria
                tc.has_pass_fail = bool(
                    re.search(r"✅\s*PASS|❌\s*FAIL", section)
                    or re.search(r"\|\s*PASS\s*\||\|\s*FAIL\s*\|", section)
                )

                # Check for health check
                tc.has_health_check = bool(
                    re.search(r"curl\s+-[fX]|curl\s+.*--max-time", section)
                    or re.search(r"```bash\s*\n.*curl", section, re.DOTALL)
                )

                # Check for rollback procedure
                tc.has_rollback = bool(
                    re.search(r"\*\*Rollback Procedure\*\*", section)
                    and re.search(r"\|\s*Step\s*\|\s*Action\s*\|\s*Command", section)
                )

                # Extract traceability
                ears_match = re.search(r"@ears:\s*(EARS\.\d+\.\d+\.\d+)", section)
                if ears_match:
                    tc.ears_ref = ears_match.group(1)

                bdd_match = re.search(r"@bdd:\s*(BDD\.\d+\.\d+\.\d+)", section)
                if bdd_match:
                    tc.bdd_ref = bdd_match.group(1)

    def _calculate_gate_scores(self) -> dict:
        """Calculate quality gate scores."""
        total_tests = len(self.test_cases) or 1

        # GATE-01: Critical Paths (all tests should be P0)
        # For STEST, all defined tests are considered critical
        critical_paths = 100 if self.test_cases else 0

        # GATE-02: Timeout Budget
        sum_timeouts = sum(tc.timeout for tc in self.test_cases)
        timeout_budget = 100 if sum_timeouts <= self.MAX_TOTAL_TIMEOUT else 0

        # GATE-03: Rollback Defined
        tests_with_rollback = sum(1 for tc in self.test_cases if tc.has_rollback)
        rollback_defined = (tests_with_rollback / total_tests) * 100

        # GATE-04: Health Checks
        tests_with_health = sum(1 for tc in self.test_cases if tc.has_health_check)
        health_checks = (tests_with_health / total_tests) * 100

        return {
            "critical_paths": critical_paths,
            "timeout_budget": timeout_budget,
            "rollback_defined": rollback_defined,
            "health_checks": health_checks,
        }

    def _collect_issues(self, gate_scores: dict) -> list:
        """Collect validation issues."""
        issues = []

        # Traceability issues
        if not self.has_ears_tag:
            issues.append("Missing @ears traceability tag (required)")
        if not self.has_bdd_tag:
            issues.append("Missing @bdd traceability tag (required)")
        if not self.has_req_tag:
            issues.append("Missing @req traceability tag (required)")

        # Timeout issues
        sum_timeouts = sum(tc.timeout for tc in self.test_cases)
        if sum_timeouts > self.MAX_TOTAL_TIMEOUT:
            issues.append(
                f"Total timeout {sum_timeouts}s exceeds max {self.MAX_TOTAL_TIMEOUT}s"
            )

        # Per-test issues
        for tc in self.test_cases:
            if tc.timeout > self.MAX_TEST_TIMEOUT:
                issues.append(f"{tc.id}: Timeout {tc.timeout}s exceeds max 60s")
            if not tc.has_pass_fail:
                issues.append(f"{tc.id}: Missing pass/fail criteria")
            if not tc.has_health_check:
                issues.append(f"{tc.id}: Missing health check command")
            if not tc.has_rollback:
                issues.append(f"{tc.id}: Missing rollback procedure")

        return issues

    def _collect_warnings(self) -> list:
        """Collect validation warnings."""
        warnings = []

        # Calculate buffer
        sum_timeouts = sum(tc.timeout for tc in self.test_cases)
        buffer = self.MAX_TOTAL_TIMEOUT - sum_timeouts
        if 0 < buffer < 30:
            warnings.append(f"Timeout buffer only {buffer}s (recommend ≥30s)")

        return warnings


def format_result(result: ValidationResult, verbose: bool = False) -> str:
    """Format validation result for output."""
    status = "✅ PASS" if result.passed else "❌ FAIL"

    output = [f"{status} {result.file_path}: {result.overall_score:.1f}%"]

    if verbose or not result.passed:
        output.append("\nQuality Gates (100% required):")
        gate_names = {
            "critical_paths": "GATE-01 Critical Paths",
            "timeout_budget": "GATE-02 Timeout Budget",
            "rollback_defined": "GATE-03 Rollback Defined",
            "health_checks": "GATE-04 Health Checks",
        }
        for gate, score in result.gate_scores.items():
            gate_status = "✅" if score >= 100 else "❌"
            output.append(f"  {gate_names[gate]}: {score:.1f}% {gate_status}")

        if result.issues:
            output.append("\nIssues (must fix all):")
            for issue in result.issues:
                output.append(f"  - {issue}")

    return "\n".join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate STEST (Smoke Test Specification) documents"
    )
    parser.add_argument("files", nargs="+", type=Path, help="STEST files to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--quality-gates", action="store_true", help="Show quality gates")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    validator = STESTValidator(verbose=args.verbose or args.quality_gates)
    results = []
    all_passed = True

    for file_path in args.files:
        result = validator.validate_file(file_path)
        results.append(result)
        if not result.passed:
            all_passed = False

        print(format_result(result, args.verbose or args.quality_gates))
        print()

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"Summary: {passed}/{total} documents passed validation")
    print("Note: STEST requires 100% compliance - no partial passes allowed")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
