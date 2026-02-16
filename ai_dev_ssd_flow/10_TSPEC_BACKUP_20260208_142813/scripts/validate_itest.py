#!/usr/bin/env python3
"""
ITEST Validator - Integration Test Specification Validation Script

Validates ITEST documents against MVP quality gates.
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
    components: Optional[str] = None
    ctr_ref: Optional[str] = None
    has_contract_table: bool = False
    has_sequence_diagram: bool = False
    has_side_effects: bool = False
    component_count: int = 1


class ITESTValidator:
    """Validator for Integration Test Specification documents."""

    PASS_THRESHOLD = 85
    WARN_THRESHOLD = 75

    GATE_WEIGHTS = {
        "ctr_coverage": 0.30,
        "contract_compliance": 0.25,
        "sequence_diagrams": 0.20,
        "side_effects": 0.15,
        "traceability": 0.10,
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_cases: list[TestCase] = []
        self.ctr_refs: set[str] = set()
        self.sys_ref: Optional[str] = None
        self.spec_ref: Optional[str] = None
        self.has_ctr_tag: bool = False
        self.has_sys_tag: bool = False
        self.has_spec_tag: bool = False

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single ITEST document."""
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
        self.ctr_refs = set()
        self.sys_ref = None
        self.spec_ref = None
        self.has_ctr_tag = False
        self.has_sys_tag = False
        self.has_spec_tag = False

    def _parse_document(self, content: str) -> None:
        """Parse ITEST document content."""
        # Extract traceability tags
        if re.search(r"@ctr:\s*CTR-\d+", content):
            self.has_ctr_tag = True
        if re.search(r"@sys:\s*SYS\.\d+\.\d+\.\d+", content):
            self.has_sys_tag = True
        if re.search(r"@spec:\s*SPEC-\d+", content):
            self.has_spec_tag = True

        # Extract CTR references
        ctr_matches = re.findall(r"CTR-\d+", content)
        self.ctr_refs = set(ctr_matches)

        # Extract test case index entries
        index_pattern = r"\|\s*(TSPEC\.\d+\.41\.\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
        for match in re.finditer(index_pattern, content):
            test_id = match.group(1).strip()
            name = match.group(2).strip()
            components = match.group(3).strip()

            # Count components (arrows indicate multiple)
            comp_count = components.count("→") + 1

            tc = TestCase(
                id=test_id, name=name, components=components, component_count=comp_count
            )
            self.test_cases.append(tc)

        self._parse_test_case_details(content)

    def _parse_test_case_details(self, content: str) -> None:
        """Parse detailed test case sections."""
        sections = re.split(r"###\s+TSPEC\.\d+\.41\.\d+:", content)

        for i, section in enumerate(sections[1:], 1):
            if i <= len(self.test_cases):
                tc = self.test_cases[i - 1]

                # Check for contract compliance table
                tc.has_contract_table = bool(
                    re.search(r"\|\s*Aspect\s*\|\s*Expected\s*\|\s*Validation", section)
                )

                # Check for sequence diagram
                tc.has_sequence_diagram = bool(
                    re.search(r"```mermaid\s*\n\s*sequenceDiagram", section)
                )

                # Check for side effects
                tc.has_side_effects = bool(
                    re.search(r"\|\s*Effect\s*\|\s*Verification", section)
                )

                # Extract CTR reference
                ctr_match = re.search(r"@ctr:\s*(CTR-\d+)", section)
                if ctr_match:
                    tc.ctr_ref = ctr_match.group(1)

    def _calculate_gate_scores(self) -> dict:
        """Calculate quality gate scores."""
        total_tests = len(self.test_cases) or 1

        # GATE-01: CTR Coverage
        tests_with_ctr = sum(1 for tc in self.test_cases if tc.ctr_ref)
        ctr_coverage = (tests_with_ctr / total_tests) * 100

        # GATE-02: Contract Compliance
        tests_with_contract = sum(1 for tc in self.test_cases if tc.has_contract_table)
        contract_compliance = (tests_with_contract / total_tests) * 100

        # GATE-03: Sequence Diagrams (only for multi-component tests)
        multi_comp_tests = [tc for tc in self.test_cases if tc.component_count > 1]
        if multi_comp_tests:
            tests_with_seq = sum(1 for tc in multi_comp_tests if tc.has_sequence_diagram)
            sequence_diagrams = (tests_with_seq / len(multi_comp_tests)) * 100
        else:
            sequence_diagrams = 100  # No multi-component tests

        # GATE-04: Side Effects
        tests_with_effects = sum(1 for tc in self.test_cases if tc.has_side_effects)
        side_effects = (tests_with_effects / total_tests) * 100

        # GATE-05: Traceability
        tags_present = sum([self.has_ctr_tag, self.has_sys_tag, self.has_spec_tag])
        traceability = (tags_present / 3) * 100

        return {
            "ctr_coverage": ctr_coverage,
            "contract_compliance": contract_compliance,
            "sequence_diagrams": sequence_diagrams,
            "side_effects": side_effects,
            "traceability": traceability,
        }

    def _collect_issues(self, gate_scores: dict) -> list:
        """Collect validation issues."""
        issues = []

        if not self.has_ctr_tag:
            issues.append("Missing @ctr traceability tag")
        if not self.has_spec_tag:
            issues.append("Missing @spec traceability tag")

        for tc in self.test_cases:
            if not tc.ctr_ref:
                issues.append(f"{tc.id}: Missing @ctr reference")
            if not tc.has_contract_table:
                issues.append(f"{tc.id}: Missing contract compliance table")
            if tc.component_count > 1 and not tc.has_sequence_diagram:
                issues.append(f"{tc.id}: Missing sequence diagram for multi-component test")

        for gate, score in gate_scores.items():
            if score < self.WARN_THRESHOLD:
                issues.append(f"GATE {gate}: Score {score:.1f}% below threshold")

        return issues

    def _collect_warnings(self) -> list:
        """Collect validation warnings."""
        warnings = []

        if not self.has_sys_tag:
            warnings.append("Missing @sys traceability tag (recommended)")

        for tc in self.test_cases:
            if not tc.has_side_effects:
                warnings.append(f"{tc.id}: Missing side effects documentation")

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
            "ctr_coverage": "GATE-01 CTR Coverage",
            "contract_compliance": "GATE-02 Contract Tables",
            "sequence_diagrams": "GATE-03 Sequence Diagrams",
            "side_effects": "GATE-04 Side Effects",
            "traceability": "GATE-05 Traceability",
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
        description="Validate ITEST (Integration Test Specification) documents"
    )
    parser.add_argument("files", nargs="+", type=Path, help="ITEST files to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--quality-gates", action="store_true", help="Show quality gates")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    validator = ITESTValidator(verbose=args.verbose or args.quality_gates)
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
