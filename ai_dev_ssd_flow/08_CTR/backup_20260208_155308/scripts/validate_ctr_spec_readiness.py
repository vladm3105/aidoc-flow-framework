#!/usr/bin/env python3
"""
CTR SPEC-Readiness Validator

Scores CTR files on completeness (0-100%) based on presence of:
- API specification (endpoints, methods)
- Data schemas (JSON Schema/Pydantic)
- Error catalog with statuses
- Versioning strategy
- Testing requirements
- Absence of placeholders
- Type annotations in examples
- Error recovery strategies
- Concrete, domain-specific examples
- Diagrams (state/sequence)

Usage:
    python validate_ctr_spec_readiness.py --ctr-file docs/08_CTR/CTR-01_iam.md
    python validate_ctr_spec_readiness.py --directory docs/08_CTR/ --min-score 90
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    file_path: Path
    score: int
    passed: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class CTRSpecReadinessValidator:
    SECTION_API = r"##\s*\d+\.\s*(API\s+Specification|Interface\s+Definition|Interface\s+Specification)"
    SECTION_DATA = r"##\s*\d+\.\s*(Data\s+Models|Data\s+Schema)"
    SECTION_ERROR = r"##\s*\d+\.\s*Error\s+Handling"
    SECTION_VERSION = r"##\s*\d+\.\s*Versioning"
    SECTION_TESTING = r"##\s*\d+\.\s*.*Testing"

    ENDPOINT_PATTERN = r"(GET|POST|PUT|DELETE|PATCH)\s+/"
    OPENAPI_PATTERN = r"openapi|swagger"

    JSON_SCHEMA_PATTERN = r'"\$schema":\s*"http://json-schema\.org'
    PYDANTIC_PATTERN = r"class\s+\w+\(BaseModel\):"
    TYPE_ANNOTATION_PATTERN = r"def\s+\w+\([^)]*:\s*\w+"

    EXCEPTION_CATALOG_PATTERN = r"\|\s*\*?\*?\s*(Exception\s+Type|Error\s+Code)\s*\*?\*?\s*\|.*\*?\*?\s*(HTTP\s+(Code|Status)|Status)\s*\*?\*?"
    STATE_DIAGRAM_PATTERN = r"```mermaid\s+stateDiagram|```mermaid\s+sequenceDiagram"

    YAML_CONFIG_PATTERN = r"```yaml"

    PLACEHOLDER_PATTERNS = [
        r"\[PLACEHOLDER\]",
        r"\[TODO\]",
        r"\[TBD\]",
        r"<insert\s+\w+>",
        r"<fill\s+in>",
        r"\.\.\."  # ellipsis
    ]

    def __init__(self, min_score: int = 90):
        self.min_score = min_score

    def validate_file(self, file_path: Path) -> ValidationResult:
        result = ValidationResult(file_path=file_path, score=0, passed=False)
        if not file_path.exists():
            result.errors.append(f"File not found: {file_path}")
            return result

        content = file_path.read_text(encoding='utf-8')

        # Core sections
        result.checks["api_spec"] = bool(re.search(self.SECTION_API, content, re.IGNORECASE))
        if not result.checks["api_spec"]:
            result.errors.append("Missing Section 2: API Specification")

        result.checks["data_models"] = bool(re.search(self.SECTION_DATA, content, re.IGNORECASE)) and (
            bool(re.search(self.JSON_SCHEMA_PATTERN, content)) or bool(re.search(self.PYDANTIC_PATTERN, content))
        )
        if not result.checks["data_models"]:
            result.warnings.append("Data models missing JSON Schema or Pydantic models")

        result.checks["error_handling"] = bool(re.search(self.SECTION_ERROR, content, re.IGNORECASE)) and bool(
            re.search(self.EXCEPTION_CATALOG_PATTERN, content)
        )
        if not result.checks["error_handling"]:
            result.warnings.append("Error handling missing exception catalog table")

        result.checks["versioning"] = bool(re.search(self.SECTION_VERSION, content, re.IGNORECASE))
        if not result.checks["versioning"]:
            result.warnings.append("Missing Versioning section")

        result.checks["testing"] = bool(re.search(self.SECTION_TESTING, content, re.IGNORECASE))
        if not result.checks["testing"]:
            result.warnings.append("Missing Testing section")

        # Additional checks
        result.checks["endpoints"] = bool(re.search(self.ENDPOINT_PATTERN, content))
        result.checks["openapi_ref"] = bool(re.search(self.OPENAPI_PATTERN, content, re.IGNORECASE))
        result.checks["no_placeholders"] = self._check_no_placeholders(content, result)
        result.checks["type_annotations"] = self._check_type_annotations(content, result)
        result.checks["error_recovery"] = self._check_error_recovery(content, result)
        result.checks["concrete_examples"] = self._check_concrete_examples(content, result)
        result.checks["diagrams"] = bool(re.search(self.STATE_DIAGRAM_PATTERN, content))

        # Score: 10 points per true check
        result.score = sum(10 for ok in result.checks.values() if ok)
        if result.errors:
            result.passed = False
        else:
            result.passed = result.score >= self.min_score

        return result

    def _check_no_placeholders(self, content: str, result: ValidationResult) -> bool:
        # Remove code blocks to avoid counting example ellipses and placeholders inside code
        stripped = re.sub(r"```[\s\S]*?```", "", content)
        hits: List[str] = []
        for pat in self.PLACEHOLDER_PATTERNS:
            m = re.findall(pat, stripped, re.IGNORECASE)
            if m:
                hits.extend(m)
        if hits:
            result.warnings.append(
                f"Found {len(hits)} placeholder(s): {', '.join(sorted(set(hits))[:3])}"
            )
            return False
        return True

    def _check_type_annotations(self, content: str, result: ValidationResult) -> bool:
        anns = re.findall(self.TYPE_ANNOTATION_PATTERN, content)
        if len(anns) < 3:
            result.warnings.append("Limited type annotations in examples (expected 3+)")
            return False
        return True

    def _check_error_recovery(self, content: str, result: ValidationResult) -> bool:
        kws = ["retry", "backoff", "fallback", "circuit breaker", "timeout", "recovery"]
        count = sum(1 for k in kws if re.search(k, content, re.IGNORECASE))
        if count < 2:
            result.warnings.append("Limited error recovery strategies documented")
            return False
        return True

    def _check_concrete_examples(self, content: str, result: ValidationResult) -> bool:
        indicators = [
            r"\b[A-Z]{2,5}\b",  # symbols
            r"\b\d{4}-\d{2}-\d{2}\b",  # dates
            r"\b\d+\.\d{2}\b",  # money
            r'"[a-z_]+":',  # json keys
            r"user_id|account_id|order_id"
        ]
        count = sum(len(re.findall(p, content)) for p in indicators)
        if count < 10:
            result.warnings.append("Limited concrete examples; add realistic domain data")
            return False
        return True

    def validate_directory(self, directory: Path) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        for f in directory.rglob("CTR-*_*.md"):
            if "_index" in f.name or "TEMPLATE" in f.name:
                continue
            results.append(self.validate_file(f))
        return results

    def print_report(self, results: List[ValidationResult]) -> None:
        print("\nCTR SPEC-READINESS VALIDATION REPORT\n")
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]
        total = len(results) or 1
        avg = sum(r.score for r in results) / total
        print(f"Total Files: {len(results)}")
        print(f"Passed (≥{self.min_score}%): {len(passed)}")
        print(f"Failed (<{self.min_score}%): {len(failed)}")
        print(f"Average Score: {avg:.1f}%\n")
        for r in results:
            status = "✅ PASS" if r.passed else "❌ FAIL"
            print(f"{status} [{r.score:3d}%] {r.file_path.name}")
            for e in r.errors:
                print(f"    ❌ ERROR: {e}")
            if not r.passed:
                for w in r.warnings:
                    print(f"    ⚠️  WARNING: {w}")
            print()


def main():
    parser = argparse.ArgumentParser(description="Validate CTR files for SPEC-readiness")
    parser.add_argument("--ctr-file", type=Path, help="Path to a CTR file")
    parser.add_argument("--directory", type=Path, help="Path to CTR directory")
    parser.add_argument("--min-score", type=int, default=90, help="Minimum score to pass")
    args = parser.parse_args()

    if not args.ctr_file and not args.directory:
        parser.error("Must specify either --ctr-file or --directory")

    validator = CTRSpecReadinessValidator(min_score=args.min_score)
    if args.ctr_file:
        results = [validator.validate_file(args.ctr_file)]
    else:
        results = validator.validate_directory(args.directory)

    if not results:
        print("No CTR files found to validate")
        sys.exit(0)

    validator.print_report(results)
    errors = [e for r in results for e in r.errors]
    if errors:
        sys.exit(2)
    if any(not r.passed for r in results):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
