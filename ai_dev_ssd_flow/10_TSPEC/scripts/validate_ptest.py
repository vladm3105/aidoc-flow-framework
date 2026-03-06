#!/usr/bin/env python3
"""
PTEST Validator - Performance Test Specification Validation Script

Validates PTEST documents against MVP quality gates.
"""

import argparse
import re
import sys
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    from jsonschema import validate as jsonschema_validate, ValidationError, SchemaError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
try:
    from error_code_helpers import format_error, format_warning, calculate_exit_code
    HAS_ERROR_CODES = True
except ImportError:
    HAS_ERROR_CODES = False



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


    def _validate_against_schema(self, file_path: Path, content: str) -> list:
        """Validate TSPEC document against MVP schema with flexible path resolution."""
        errors = []
        if not HAS_JSONSCHEMA:
            return errors

        filename = file_path.name
        type_match = re.match(r'^(UTEST|ITEST|STEST|FTEST|PTEST|SECTEST)-', filename)
        if not type_match:
            errors.append(f"Cannot determine test type from filename: {filename}")
            return errors

        type_name = type_match.group(1)
        schema_candidates = [
            file_path.parents[1] / f"{type_name}_MVP_SCHEMA.yaml",
            file_path.parent / f"{type_name}_MVP_SCHEMA.yaml",
            file_path.parents[2] / type_name / f"{type_name}_MVP_SCHEMA.yaml" if len(file_path.parents) > 2 else None,
        ]

        current = file_path.parent
        search_depth = 0
        while current.name and current.name not in ['TSPEC', '10_TSPEC', '/'] and search_depth < 5:
            schema_candidates.append(current / type_name / f"{type_name}_MVP_SCHEMA.yaml")
            current = current.parent
            search_depth += 1
            if current == current.parent:
                break

        schema_file = None
        for candidate in schema_candidates:
            if candidate and candidate.exists():
                schema_file = candidate
                break

        if not schema_file:
            if self.verbose:
                print(f"  Note: Schema file not found for {type_name}")
            return errors

        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = yaml.safe_load(f)

            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                errors.append("No YAML frontmatter found")
                return errors

            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            jsonschema_validate(instance=frontmatter, schema=schema)

        except yaml.YAMLError as e:
            errors.append(f"YAML parsing error: {e}")
        except ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
        except SchemaError as e:
            errors.append(f"Invalid schema: {e}")
        except Exception as e:
            errors.append(f"Unexpected error during schema validation: {e}")

        return errors


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

        # Schema validation (before other checks)
        schema_errors = self._validate_against_schema(file_path, content)
        if schema_errors:
            return ValidationResult(
                file_path=str(file_path),
                passed=False,
                overall_score=0,
                issues=schema_errors,
            )

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
        """Collect validation issues with error codes."""
        issues = []

        # Traceability checks
        if not self.spec_ref:
            if HAS_ERROR_CODES:
                issues.append(format_error("TSPEC-E007", "missing @spec reference"))
            else:
                issues.append("Missing @spec reference in document")

        if not self.sys_refs:
            if HAS_ERROR_CODES:
                issues.append(format_error("TSPEC-E007", "missing @sys references"))
            else:
                issues.append("No @sys references found in document")

        # Execution profile check
        if not self.has_execution_profile:
            if HAS_ERROR_CODES:
                issues.append(format_error("PTEST-E001", "missing execution_profile section"))
            else:
                issues.append("Missing execution_profile section")

        # Test case checks
        for tc in self.test_cases:
            if not tc.sys_ref:
                if HAS_ERROR_CODES:
                    issues.append(format_error("TSPEC-E007", f"{tc.id} - missing @sys reference"))
                else:
                    issues.append(f"{tc.id}: Missing @sys reference")

            if not tc.has_load_scenarios:
                if HAS_ERROR_CODES:
                    issues.append(format_error("PTEST-E001", f"{tc.id} - missing load scenarios"))
                else:
                    issues.append(f"{tc.id}: Missing load scenarios table")

            if tc.category not in self.VALID_CATEGORIES:
                if HAS_ERROR_CODES:
                    issues.append(format_error("PTEST-E003", f"{tc.id} - invalid category"))
                else:
                    issues.append(f"{tc.id}: Invalid or missing category prefix")

        # Quality gate checks
        overall_score = sum(gate_scores.values()) / len(gate_scores) if gate_scores else 0
        if overall_score < 85:
            if HAS_ERROR_CODES:
                issues.append(format_error("PTEST-W001", f"overall score {overall_score:.1f}% < 85%"))

        for gate, score in gate_scores.items():
            if score < self.WARN_THRESHOLD:
                if HAS_ERROR_CODES:
                    issues.append(format_error("TSPEC-E009", f"{gate} {score:.1f}% < 75%"))
                else:
                    issues.append(f"GATE {gate}: Score {score:.1f}% below threshold")

        return issues

    def _collect_warnings(self, gate_scores: dict) -> list:
        """Collect validation warnings with error codes."""
        warnings = []

        for tc in self.test_cases:
            if not tc.has_thresholds:
                warnings.append(f"{tc.id}: Missing performance thresholds")

            if not tc.has_measurement_strategy:
                if HAS_ERROR_CODES:
                    warnings.append(format_warning("PTEST-W001", f"{tc.id} - missing measurement strategy"))
                else:
                    warnings.append(f"{tc.id}: Missing measurement strategy")

        return warnings


def format_result(result: ValidationResult, verbose: bool = False) -> str:
    """Format validation result for output."""
    status = "[PASS] PASS" if result.passed else "[FAIL] FAIL"
    if not result.passed and result.overall_score >= 75:
        status = "[WARN] WARN"

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
            gate_status = "[PASS]" if score >= 75 else "[FAIL]"
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
    print(f"Summary: {passed}/{total} documents passed validation")    # Calculate exit code based on errors and warnings
    if HAS_ERROR_CODES:
        # Collect all issues and warnings from results
        all_issues = []
        all_warnings = []
        for r in results:
            all_issues.extend(r.issues)
            all_warnings.extend(r.warnings)
        exit_code = calculate_exit_code(all_issues, all_warnings)
        sys.exit(exit_code)
    else:
        sys.exit(0 if all_passed else 1)



if __name__ == "__main__":
    main()
