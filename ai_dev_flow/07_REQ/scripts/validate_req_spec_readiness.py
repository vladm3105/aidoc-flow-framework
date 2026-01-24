#!/usr/bin/env python3
"""
REQ SPEC-Readiness Validator

Validates REQ V2 documents for SPEC-generation readiness.
Scores REQ files on completeness (0-100%) based on presence of:
- Interface definitions with type signatures
- Data schemas (JSON Schema/Pydantic/SQLAlchemy)
- Error catalog with recovery strategies
- Configuration examples with validation
- Quality attributes
- No placeholders

Usage:
    python validate_req_spec_readiness.py --req-file REQ/api/REQ-01.md
    python validate_req_spec_readiness.py --directory REQ/
    python validate_req_spec_readiness.py --req-file REQ/api/REQ-01.md --min-score 90
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of REQ SPEC-readiness validation."""
    file_path: Path
    score: int
    passed: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class REQSpecReadinessValidator:
    """Validator for REQ V2 SPEC-readiness."""

    # Section patterns
    SECTION_INTERFACE = r"##\s*4\.\s*Interface\s+Definition"
    SECTION_DATA = r"Data\s+Schema"
    SECTION_ERROR = r"##\s*5\.\s*Error\s+Handling"
    SECTION_QUALITY = r"##\s*6\.\s*Quality\s+Attributes"
    SECTION_CONFIG = r"##\s*7\.\s*Configuration"
    SECTION_TESTING = r"##\s*8\.\s*Testing\s+Requirements"

    # Content patterns
    PROTOCOL_PATTERN = r"class\s+\w+\(Protocol\):"
    ABC_PATTERN = r"class\s+\w+\(ABC\):"
    TYPE_ANNOTATION_PATTERN = r"def\s+\w+\([^)]*:\s*\w+"

    JSON_SCHEMA_PATTERN = r'"\$schema":\s*"http://json-schema\.org'
    PYDANTIC_PATTERN = r"class\s+\w+\(BaseModel\):"
    SQLALCHEMY_PATTERN = r"class\s+\w+\(Base\):"

    EXCEPTION_CATALOG_PATTERN = r"\|\s*(Exception\s+Type|Error\s+Code)\s*\|.*(HTTP\s+(Code|Status)|Status)"
    STATE_MACHINE_PATTERN = r"```mermaid\s+stateDiagram"

    YAML_CONFIG_PATTERN = r"```yaml"
    PYDANTIC_SETTINGS_PATTERN = r"class\s+\w+\(BaseSettings\):"

    # Placeholder patterns (should be absent)
    PLACEHOLDER_PATTERNS = [
        r"\[PLACEHOLDER\]",
        r"\[TODO\]",
        r"\[TBD\]",
        r"<insert\s+\w+>",
        r"<fill\s+in>",
        r"\.\.\."  # Ellipsis in code examples
    ]

    # Performance target patterns
    PERFORMANCE_PATTERN = r"(p\d+|latency|throughput|availability).*\d+"

    def __init__(self, min_score: int = 90):
        """Initialize validator with minimum passing score."""
        self.min_score = min_score

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single REQ file for SPEC-readiness."""
        result = ValidationResult(
            file_path=file_path,
            score=0,
            passed=False
        )

        if not file_path.exists():
            result.errors.append(f"File not found: {file_path}")
            return result

        content = file_path.read_text(encoding='utf-8')

        # Check each section (10 points each = 60 points)
        result.checks["section_interfaces"] = self._check_interface(content, result)
        result.checks["section_data_schemas"] = self._check_data_schema(content, result)
        result.checks["section_errors"] = self._check_error(content, result)
        result.checks["section_quality"] = self._check_quality(content, result)
        result.checks["section_config"] = self._check_config(content, result)
        result.checks["section_testing"] = self._check_testing(content, result)
        result.checks["no_placeholders"] = self._check_no_placeholders(content, result)

        # Additional quality checks (10 points each = 40 points)
        result.checks["type_annotations"] = self._check_type_annotations(content, result)
        result.checks["error_recovery"] = self._check_error_recovery(content, result)
        result.checks["concrete_examples"] = self._check_concrete_examples(content, result)
        result.checks["state_machines"] = self._check_state_machines(content, result)

        # Calculate score
        result.score = sum(10 for check in result.checks.values() if check)
        result.passed = result.score >= self.min_score

        return result

    def _check_interface(self, content: str, result: ValidationResult) -> bool:
        """Check Section 4: Interface Definition (Protocol/ABC)."""
        if not re.search(self.SECTION_INTERFACE, content, re.IGNORECASE):
            result.errors.append("Missing Section 4: Interface Definition")
            return False

        has_protocol = bool(re.search(self.PROTOCOL_PATTERN, content))
        has_abc = bool(re.search(self.ABC_PATTERN, content))

        if not (has_protocol or has_abc):
            result.warnings.append("Section 4 missing Protocol or ABC definitions")
            return False

        return True

    def _check_data_schema(self, content: str, result: ValidationResult) -> bool:
        """Check presence of Data Schema (within Section 4)."""

        has_data_heading = bool(re.search(self.SECTION_DATA, content, re.IGNORECASE))
        has_json_schema = bool(re.search(self.JSON_SCHEMA_PATTERN, content))
        has_pydantic = bool(re.search(self.PYDANTIC_PATTERN, content))

        if not has_data_heading:
            result.warnings.append("Section 4 missing Data Schema subsection")
        if not (has_json_schema or has_pydantic):
            result.errors.append("Data Schema missing JSON Schema or Pydantic models")
            return False

        return True

    def _check_error(self, content: str, result: ValidationResult) -> bool:
        """Check Section 5: Error Handling."""
        if not re.search(self.SECTION_ERROR, content, re.IGNORECASE):
            result.errors.append("Missing Section 5: Error Handling")
            return False

        has_exception_catalog = bool(re.search(self.EXCEPTION_CATALOG_PATTERN, content))

        if not has_exception_catalog:
            result.warnings.append("Section 5 missing exception catalog table")
            return False

        return True

    def _check_quality(self, content: str, result: ValidationResult) -> bool:
        """Check Section 6: Quality Attributes."""
        if not re.search(self.SECTION_QUALITY, content, re.IGNORECASE):
            result.errors.append("Missing Section 6: Quality Attributes")
            return False

        has_performance_targets = bool(re.search(self.PERFORMANCE_PATTERN, content))

        if not has_performance_targets:
            result.warnings.append("Section 6 missing quantified performance targets")
            return False

        return True

    def _check_config(self, content: str, result: ValidationResult) -> bool:
        """Check Section 7: Configuration."""
        if not re.search(self.SECTION_CONFIG, content, re.IGNORECASE):
            result.errors.append("Missing Section 7: Configuration")
            return False

        has_yaml = bool(re.search(self.YAML_CONFIG_PATTERN, content))

        if not has_yaml:
            result.warnings.append("Section 7 missing YAML configuration examples")
            return False

        return True

    def _check_testing(self, content: str, result: ValidationResult) -> bool:
        """Check Section 8: Testing Requirements."""
        if not re.search(self.SECTION_TESTING, content, re.IGNORECASE):
            result.errors.append("Missing Section 8: Testing Requirements")
            return False
        return True

    def _check_no_placeholders(self, content: str, result: ValidationResult) -> bool:
        """Check that document contains no placeholders."""
        found_placeholders = []

        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found_placeholders.extend(matches)

        if found_placeholders:
            result.warnings.append(
                f"Found {len(found_placeholders)} placeholder(s): "
                f"{', '.join(set(found_placeholders[:3]))}"
            )
            return False

        return True

    def _check_type_annotations(self, content: str, result: ValidationResult) -> bool:
        """Check for comprehensive type annotations."""
        type_annotations = re.findall(self.TYPE_ANNOTATION_PATTERN, content)

        if len(type_annotations) < 3:
            result.warnings.append(
                f"Limited type annotations found ({len(type_annotations)}). "
                "Expected 3+ annotated functions"
            )
            return False

        return True

    def _check_error_recovery(self, content: str, result: ValidationResult) -> bool:
        """Check for error recovery strategies."""
        recovery_keywords = [
            "retry", "recovery", "fallback", "circuit breaker",
            "exponential backoff", "error handling"
        ]

        recovery_count = sum(
            1 for keyword in recovery_keywords
            if re.search(keyword, content, re.IGNORECASE)
        )

        if recovery_count < 2:
            result.warnings.append(
                "Limited error recovery strategies documented. "
                "Expected retry policies, fallbacks, or circuit breakers"
            )
            return False

        return True

    def _check_concrete_examples(self, content: str, result: ValidationResult) -> bool:
        """Check for concrete examples vs generic placeholders."""
        # Look for domain-specific terminology
        domain_indicators = [
            r"[A-Z]{2,5}",  # Stock symbols (AAPL, GOOGL)
            r"\d+\.\d{2}",  # Monetary values (100.50)
            r"\d{4}-\d{2}-\d{2}",  # Dates (2025-01-09)
            r'"[a-z_]+":',  # JSON keys
            r"user_id|order_id|account_id"  # Common identifiers
        ]

        example_count = sum(
            len(re.findall(pattern, content))
            for pattern in domain_indicators
        )

        if example_count < 10:
            result.warnings.append(
                f"Limited concrete examples ({example_count} indicators). "
                "Use realistic domain-specific data"
            )
            return False

        return True

    def _check_state_machines(self, content: str, result: ValidationResult) -> bool:
        """Check for Mermaid state machine diagrams."""
        has_state_machine = bool(re.search(self.STATE_MACHINE_PATTERN, content))

        if not has_state_machine:
            result.warnings.append(
                "No Mermaid state machine diagrams found. "
                "Add state machines for complex workflows"
            )
            return False

        return True

    def validate_directory(self, directory: Path) -> List[ValidationResult]:
        """Validate all REQ files in a directory."""
        results = []

        for req_file in directory.rglob("REQ-*.md"):
            # Skip archived files
            if "archived" in str(req_file).lower():
                continue

            result = self.validate_file(req_file)
            results.append(result)

        return results

    def print_report(self, results: List[ValidationResult]) -> None:
        """Print validation report."""
        print("\n" + "=" * 80)
        print("REQ SPEC-READINESS VALIDATION REPORT")
        print("=" * 80 + "\n")

        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]

        print(f"Total Files: {len(results)}")
        print(f"Passed (≥{self.min_score}%): {len(passed)}")
        print(f"Failed (<{self.min_score}%): {len(failed)}")
        print(f"Average Score: {sum(r.score for r in results) / len(results):.1f}%\n")

        # Detailed results
        for result in results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} [{result.score:3d}%] {result.file_path.name}")

            if result.errors:
                for error in result.errors:
                    print(f"    ❌ ERROR: {error}")

            if result.warnings and not result.passed:
                for warning in result.warnings:
                    print(f"    ⚠️  WARNING: {warning}")

            print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate REQ V2 files for SPEC-generation readiness"
    )
    parser.add_argument(
        "--req-file",
        type=Path,
        help="Path to specific REQ file to validate"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        help="Path to directory containing REQ files"
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=90,
        help="Minimum SPEC-ready score (0-100, default: 90)"
    )

    args = parser.parse_args()

    if not args.req_file and not args.directory:
        parser.error("Must specify either --req-file or --directory")

    validator = REQSpecReadinessValidator(min_score=args.min_score)

    if args.req_file:
        results = [validator.validate_file(args.req_file)]
    else:
        results = validator.validate_directory(args.directory)

    if not results:
        print("No REQ files found to validate")
        sys.exit(0)

    validator.print_report(results)

    # Exit with error code if any validations failed
    if any(not r.passed for r in results):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
