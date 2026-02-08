#!/usr/bin/env python3
"""
SECTEST Validator - Security Test Specification Validation Script

Validates SECTEST documents against MVP quality gates.
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
    sec_ref: Optional[str] = None
    has_threat_scenario: bool = False
    has_security_controls: bool = False
    has_compliance_mapping: bool = False


class SECTESTValidator:
    """Validator for Security Test Specification documents."""

    VALID_CATEGORIES = ["[AuthN]", "[AuthZ]", "[Input]", "[Crypto]", "[Config]", "[Session]"]
    PASS_THRESHOLD = 90
    WARN_THRESHOLD = 80

    # Quality gate weights
    GATE_WEIGHTS = {
        "sec_coverage": 0.30,
        "threat_scenarios": 0.25,
        "security_controls": 0.20,
        "execution_profile": 0.15,
        "compliance_mapping": 0.10,
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_cases: list[TestCase] = []
        self.sec_refs: set[str] = set()
        self.spec_ref: Optional[str] = None
        self.has_execution_profile: bool = False
        self.has_safety_constraints: bool = False

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single SECTEST document."""
        if not file_path.exists():
            return ValidationResult(
                file_path=str(file_path),
                passed=False,
                overall_score=0,
                issues=[f"File not found: {file_path}"],
            )

        content = file_path.read_text(encoding="utf-8")
        self.test_cases = []
        self.sec_refs = set()
        self.spec_ref = None
        self.has_execution_profile = False
        self.has_safety_constraints = False

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
        """Parse SECTEST document content."""
        # Extract SPEC reference
        spec_match = re.search(r"@spec:\s*(SPEC-\d+)", content)
        if spec_match:
            self.spec_ref = spec_match.group(1)

        # Extract SEC references
        sec_matches = re.findall(r"@sec:\s*(SEC\.\d+\.\d+)", content)
        self.sec_refs = set(sec_matches)

        # Check for execution profile
        self.has_execution_profile = "execution_profile:" in content
        
        # Check for safety constraints in skip_policy rationale
        skip_policy_match = re.search(r"skip_policy:.*?rationale:\s*\"([^\"]+)\"", content, re.DOTALL)
        if skip_policy_match:
            rationale = skip_policy_match.group(1).lower()
            self.has_safety_constraints = any(word in rationale for word in ["safety", "isolated", "environment", "damage"])

        # Extract test case index entries
        index_pattern = r"\|\s*(TSPEC\.\d+\.45\.\d+)\s*\|\s*([^|]+)\s*\|\s*(\[?\w+\]?)\s*\|"
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
        sections = re.split(r"###\s+TSPEC\.\d+\.45\.\d+:", content)

        for i, section in enumerate(sections[1:], 1):
            if i <= len(self.test_cases):
                tc = self.test_cases[i - 1]

                # Check for threat scenario table
                tc.has_threat_scenario = bool(
                    re.search(r"\|\s*Threat Actor\s*\|\s*Attack Vector", section)
                )

                # Check for security controls table
                tc.has_security_controls = bool(
                    re.search(r"\|\s*Control\s*\|\s*Expected Behavior", section)
                )

                # Check for compliance mapping
                tc.has_compliance_mapping = bool(
                    re.search(r"\*\*OWASP\*\*|\*\*CWE\*\*|\*\*NIST\*\*", section)
                )

                # Extract SEC reference
                sec_match = re.search(r"@sec:\s*(SEC\.\d+\.\d+)", section)
                if sec_match:
                    tc.sec_ref = sec_match.group(1)

    def _calculate_gate_scores(self) -> dict:
        """Calculate quality gate scores."""
        total_tests = len(self.test_cases) or 1

        # GATE-01: SEC Coverage
        tests_with_sec = sum(1 for tc in self.test_cases if tc.sec_ref)
        sec_coverage = (tests_with_sec / total_tests) * 100

        # GATE-02: Threat Scenarios
        tests_with_threat = sum(1 for tc in self.test_cases if tc.has_threat_scenario)
        threat_scenarios = (tests_with_threat / total_tests) * 100

        # GATE-03: Security Controls
        tests_with_controls = sum(1 for tc in self.test_cases if tc.has_security_controls)
        security_controls = (tests_with_controls / total_tests) * 100

        # GATE-04: Execution Profile
        if self.has_execution_profile and self.has_safety_constraints:
            execution_profile = 100.0
        elif self.has_execution_profile:
            execution_profile = 50.0
        else:
            execution_profile = 0.0

        # GATE-05: Compliance Mapping
        tests_with_compliance = sum(1 for tc in self.test_cases if tc.has_compliance_mapping)
        compliance_mapping = (tests_with_compliance / total_tests) * 100

        return {
            "sec_coverage": sec_coverage,
            "threat_scenarios": threat_scenarios,
            "security_controls": security_controls,
            "execution_profile": execution_profile,
            "compliance_mapping": compliance_mapping,
        }

    def _collect_issues(self, gate_scores: dict) -> list:
        """Collect validation issues."""
        issues = []

        # Check for missing SPEC reference
        if not self.spec_ref:
            issues.append("Missing @spec reference in document")

        # Check for missing SEC references
        if not self.sec_refs:
            issues.append("No @sec references found in document")

        # Check for missing execution profile
        if not self.has_execution_profile:
            issues.append("Missing execution_profile section")

        # Check for missing safety constraints
        if self.has_execution_profile and not self.has_safety_constraints:
            issues.append("Missing safety constraints in execution_profile (isolated environment requirement)")

        # Check individual test cases
        for tc in self.test_cases:
            if not tc.sec_ref:
                issues.append(f"{tc.id}: Missing @sec reference")
            if not tc.has_threat_scenario:
                issues.append(f"{tc.id}: Missing threat scenario")
            if not tc.has_security_controls:
                issues.append(f"{tc.id}: Missing security controls")
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
            if not tc.has_compliance_mapping:
                warnings.append(f"{tc.id}: Missing compliance mapping (OWASP/CWE)")

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
            "sec_coverage": "GATE-01 SEC Coverage",
            "threat_scenarios": "GATE-02 Threat Scenarios",
            "security_controls": "GATE-03 Security Controls",
            "execution_profile": "GATE-04 Execution Profile",
            "compliance_mapping": "GATE-05 Compliance Mapping",
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
        description="Validate SECTEST (Security Test Specification) documents"
    )
    parser.add_argument("files", nargs="+", type=Path, help="SECTEST files to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--quality-gates", action="store_true", help="Show quality gate breakdown"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    validator = SECTESTValidator(verbose=args.verbose or args.quality_gates)
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
