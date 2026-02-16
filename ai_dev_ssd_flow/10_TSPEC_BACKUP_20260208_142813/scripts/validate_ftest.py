#!/usr/bin/env python3
"""
FTEST Validator - Functional Test Specification Validation Script

Validates FTEST documents against MVP quality gates.
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
    quality_attribute: Optional[str] = None
    sys_ref: Optional[str] = None
    threshold_ref: Optional[str] = None
    has_threshold_table: bool = False
    has_workflow: bool = False
    has_measurement: bool = False


class FTESTValidator:
    """Validator for Functional Test Specification documents."""

    PASS_THRESHOLD = 85
    WARN_THRESHOLD = 75

    GATE_WEIGHTS = {
        "sys_coverage": 0.30,
        "threshold_refs": 0.25,
        "workflow_steps": 0.25,
        "measurement": 0.20,
    }

    QUALITY_ATTRIBUTES = ["Performance", "Reliability", "Security", "Scalability"]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_cases: list[TestCase] = []
        self.sys_refs: set[str] = set()
        self.threshold_refs: set[str] = set()
        self.has_sys_tag: bool = False
        self.has_threshold_tag: bool = False

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single FTEST document."""
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
        self.sys_refs = set()
        self.threshold_refs = set()
        self.has_sys_tag = False
        self.has_threshold_tag = False

    def _parse_document(self, content: str) -> None:
        """Parse FTEST document content."""
        # Extract traceability tags
        if re.search(r"@sys:\s*SYS\.\d+\.\d+\.\d+", content):
            self.has_sys_tag = True
        if re.search(r"@threshold:\s*TH-[A-Z]+-\d+", content):
            self.has_threshold_tag = True

        # Extract SYS references
        sys_matches = re.findall(r"SYS\.\d+\.\d+\.\d+", content)
        self.sys_refs = set(sys_matches)

        # Extract threshold references
        threshold_matches = re.findall(r"TH-[A-Z]+-\d+", content)
        self.threshold_refs = set(threshold_matches)

        # Extract test case index entries
        index_pattern = r"\|\s*(TSPEC\.\d+\.43\.\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
        for match in re.finditer(index_pattern, content):
            test_id = match.group(1).strip()
            name = match.group(2).strip()
            quality_attr = match.group(3).strip()
            sys_coverage = match.group(4).strip()

            tc = TestCase(
                id=test_id,
                name=name,
                quality_attribute=quality_attr,
                sys_ref=sys_coverage if "SYS" in sys_coverage else None,
            )
            self.test_cases.append(tc)

        self._parse_test_case_details(content)

    def _parse_test_case_details(self, content: str) -> None:
        """Parse detailed test case sections."""
        sections = re.split(r"###\s+TSPEC\.\d+\.43\.\d+:", content)

        for i, section in enumerate(sections[1:], 1):
            if i <= len(self.test_cases):
                tc = self.test_cases[i - 1]

                # Check for threshold validation table
                tc.has_threshold_table = bool(
                    re.search(r"\|\s*Metric\s*\|\s*Threshold\s*\|\s*Measurement", section)
                )

                # Check for workflow steps
                tc.has_workflow = bool(
                    re.search(r"\|\s*Step\s*\|\s*Action\s*\|\s*Expected Result", section)
                )

                # Check for measurement methodology
                tc.has_measurement = bool(
                    re.search(r"```python|```\n.*assert", section, re.DOTALL)
                )

                # Extract threshold reference
                threshold_match = re.search(r"@threshold:\s*(TH-[A-Z]+-\d+)", section)
                if threshold_match:
                    tc.threshold_ref = threshold_match.group(1)

                # Extract SYS reference
                sys_match = re.search(r"@sys:\s*(SYS\.\d+\.\d+\.\d+)", section)
                if sys_match:
                    tc.sys_ref = sys_match.group(1)

    def _calculate_gate_scores(self) -> dict:
        """Calculate quality gate scores."""
        total_tests = len(self.test_cases) or 1

        # GATE-01: SYS Coverage
        tests_with_sys = sum(1 for tc in self.test_cases if tc.sys_ref)
        sys_coverage = (tests_with_sys / total_tests) * 100

        # GATE-02: Threshold Refs
        tests_with_threshold = sum(1 for tc in self.test_cases if tc.threshold_ref)
        threshold_refs = (tests_with_threshold / total_tests) * 100

        # GATE-03: Workflow Steps
        tests_with_workflow = sum(1 for tc in self.test_cases if tc.has_workflow)
        workflow_steps = (tests_with_workflow / total_tests) * 100

        # GATE-04: Measurement
        tests_with_measurement = sum(1 for tc in self.test_cases if tc.has_measurement)
        measurement = (tests_with_measurement / total_tests) * 100

        return {
            "sys_coverage": sys_coverage,
            "threshold_refs": threshold_refs,
            "workflow_steps": workflow_steps,
            "measurement": measurement,
        }

    def _collect_issues(self, gate_scores: dict) -> list:
        """Collect validation issues."""
        issues = []

        if not self.has_sys_tag:
            issues.append("Missing @sys traceability tag")
        if not self.has_threshold_tag:
            issues.append("Missing @threshold traceability tag")

        for tc in self.test_cases:
            if not tc.sys_ref:
                issues.append(f"{tc.id}: Missing @sys reference")
            if not tc.threshold_ref:
                issues.append(f"{tc.id}: Missing @threshold reference")
            if not tc.has_threshold_table:
                issues.append(f"{tc.id}: Missing threshold validation table")
            if not tc.has_workflow:
                issues.append(f"{tc.id}: Missing workflow steps")

        for gate, score in gate_scores.items():
            if score < self.WARN_THRESHOLD:
                issues.append(f"GATE {gate}: Score {score:.1f}% below threshold")

        return issues

    def _collect_warnings(self) -> list:
        """Collect validation warnings."""
        warnings = []

        for tc in self.test_cases:
            if not tc.has_measurement:
                warnings.append(f"{tc.id}: Missing measurement methodology (recommended)")

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
            "threshold_refs": "GATE-02 Threshold Refs",
            "workflow_steps": "GATE-03 Workflow Steps",
            "measurement": "GATE-04 Measurement",
        }
        for gate, score in result.gate_scores.items():
            gate_status = "✅" if score >= 75 else "❌"
            output.append(f"  {gate_names[gate]}: {score:.1f}% {gate_status}")

        if result.issues:
            output.append("\nIssues:")
            for issue in result.issues[:10]:
                output.append(f"  - {issue}")

    return "\n".join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate FTEST (Functional Test Specification) documents"
    )
    parser.add_argument("files", nargs="+", type=Path, help="FTEST files to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--quality-gates", action="store_true", help="Show quality gates")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    validator = FTESTValidator(verbose=args.verbose or args.quality_gates)
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

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
