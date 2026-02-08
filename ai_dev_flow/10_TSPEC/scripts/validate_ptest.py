#!/usr/bin/env python3
"""
PTEST Validator - Performance Test Specification Validation Script

Validates PTEST documents against MVP quality gates.
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
    sys_ref: Optional[str] = None
    has_load_scenarios: bool = False
    has_thresholds: bool = False
    has_measurement_strategy: bool = False


class PTESTValidator:
    """Validator for Performance Test Specification documents."""

    VALID_CATEGORIES = ["[Load]", "[Stress]", "[Endurance]", "[Spike]"]
    PASS_THRESHOLD = 85
    WARN_THRESHOLD = 75

    # Quality gate weights
    GATE_WEIGHTS = {
        "sys_coverage": 0.25,
        "load_scenarios": 0.25,
        "thresholds": 0.20,
        "execution_profile": 0.15,
        "measurement_strategy": 0.15,
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_cases: list[TestCase] = []
        self.sys_refs: set[str] = set()
        self.spec_ref: Optional[str] = None
        self.has_execution_profile: bool = False

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single PTEST document."""
        if not file_path.exists():
            return ValidationResult(
                file_path=str(file_path),
                passed=False,
                overall_score=0,
                issues=[f"File not found: {file_path}"],
            )

        content = file_path.read_text(encoding="utf-8")
        self.test_cases = []
        self.sys_refs = set()
        self.spec_ref = None
        self.has_execution_profile = False

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
        """Parse PTEST document content."""
        # Extract SPEC reference
        spec_match = re.search(r"@spec:\s*(SPEC-\d+)", content)
        if spec_match:
            self.spec_ref = spec_match.group(1)

        # Extract SYS references
        sys_matches = re.findall(r"@sys:\s*(SYS\.\d+\.\d+)", content)
        self.sys_refs = set(sys_matches)

        # Check for execution profile
        self.has_execution_profile = "execution_profile:" in content

        # Extract test case index entries
        index_pattern = r"\|\s*(TSPEC\.\d+\.44\.\d+)\s*\|\s*([^|]+)\s*\|\s*(\[?\w+\]?)\s*\|"
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
        sections = re.split(r"###\s+TSPEC\.\d+\.44\.\d+:", content)

        for i, section in enumerate(sections[1:], 1):
            if i <= len(self.test_cases):
                tc = self.test_cases[i - 1]

                # Check for load scenarios table
                tc.has_load_scenarios = bool(
                    re.search(r"\|\s*Load Level\s*\|\s*Concurrent Users", section)
                )

                # Check for thresholds table
                tc.has_thresholds = bool(
                    re.search(r"\|\s*Metric\s*\|\s*Target", section)
                )

                # Check for measurement strategy
                tc.has_measurement_strategy = bool(
                    re.search(r"\*\*Measurement Strategy\*\*", section)
                )

                # Extract SYS reference
                sys_match = re.search(r"@sys:\s*(SYS\.\d+\.\d+)", section)
                if sys_match:
                    tc.sys_ref = sys_match.group(1)

    def _calculate_gate_scores(self) -> dict:
        """Calculate quality gate scores."""
        total_tests = len(self.test_cases) or 1

        # GATE-01: SYS Coverage
        tests_with_sys = sum(1 for tc in self.test_cases if tc.sys_ref)
        sys_coverage = (tests_with_sys / total_tests) * 100

        # GATE-02: Load Scenarios
        tests_with_load = sum(1 for tc in self.test_cases if tc.has_load_scenarios)
        load_scenarios = (tests_with_load / total_tests) * 100

        # GATE-03: Thresholds
        tests_with_thresholds = sum(1 for tc in self.test_cases if tc.has_thresholds)
        thresholds = (tests_with_thresholds / total_tests) * 100

        # GATE-04: Execution Profile
        execution_profile = 100.0 if self.has_execution_profile else 0.0

        # GATE-05: Measurement Strategy
        tests_with_strategy = sum(1 for tc in self.test_cases if tc.has_measurement_strategy)
        measurement_strategy = (tests_with_strategy / total_tests) * 100

        return {
            "sys_coverage": sys_coverage,
            "load_scenarios": load_scenarios,
            "thresholds": thresholds,
            "execution_profile": execution_profile,
            "measurement_strategy": measurement_strategy,
        }

    def _collect_issues(self, gate_scores: dict) -> list:
        """Collect validation issues."""
        issues = []

        # Check for missing SPEC reference
        if not self.spec_ref:
            issues.append("Missing @spec reference in document")

        # Check for missing SYS references
        if not self.sys_refs:
            issues.append("No @sys references found in document")

        # Check for missing execution profile
        if not self.has_execution_profile:
            issues.append("Missing execution_profile section")

        # Check individual test cases
        for tc in self.test_cases:
            if not tc.sys_ref:
                issues.append(f"{tc.id}: Missing @sys reference")
            if not tc.has_load_scenarios:
                issues.append(f"{tc.id}: Missing load scenarios table")
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
            if not tc.has_thresholds:
                warnings.append(f"{tc.id}: Missing performance thresholds")
            if not tc.has_measurement_strategy:
                warnings.append(f"{tc.id}: Missing measurement strategy")

        return warnings


def format_result(result: ValidationResult, verbose: bool = False) -> str:
    """Format validation result for output."""
    status = "✅ PASS" if result.passed else "❌ FAIL"
    if not result.passed and result.overall_score >= 75:
        status = "⚠️ WARN"

    output = [f"{status} {result.file_path}: {result.overall_score:.1f}%"]

    if verbose:
        output.append("\nQuality Gates:")
        gate_names = {
            "sys_coverage": "GATE-01 SYS Coverage",
            "load_scenarios": "GATE-02 Load Scenarios",
            "thresholds": "GATE-03 Thresholds",
            "execution_profile": "GATE-04 Execution Profile",
            "measurement_strategy": "GATE-05 Measurement Strategy",
        }
        for gate, score in result.gate_scores.items():
            gate_status = "✅" if score >= 75 else "❌"
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
        description="Validate PTEST (Performance Test Specification) documents"
    )
    parser.add_argument("files", nargs="+", type=Path, help="PTEST files to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--quality-gates", action="store_true", help="Show quality gate breakdown"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    validator = PTESTValidator(verbose=args.verbose or args.quality_gates)
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
