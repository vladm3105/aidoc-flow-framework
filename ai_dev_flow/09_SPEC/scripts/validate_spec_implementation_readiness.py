#!/usr/bin/env python3
"""
SPEC Implementation Readiness Validator

Scores SPEC files on implementation readiness (0-100%) based on presence of:
- Complete architecture specification (component structure, dependencies)
- Interface definitions with full request/response schemas
- Behavior specifications (state machines, algorithms, error handling)
- Performance targets (latency, throughput, resource limits)
- Security specifications (authentication, authorization, encryption)
- Observability requirements (logging, metrics, tracing)
- Verification approach (test strategies, contract tests)
- Implementation details (configuration, deployment, scaling)
- REQ-to-implementation mapping (every REQ has corresponding implementation)
- Concrete code examples (pseudocode, API examples, data models)

Usage:
    python validate_spec_implementation_readiness.py --spec-file docs/09_SPEC/SPEC-01_iam.yaml
    python validate_spec_implementation_readiness.py --directory docs/09_SPEC/ --min-score 90
    python validate_spec_implementation_readiness.py --directory docs/09_SPEC/ --min-score 80
"""

import argparse
import re
import sys
import yaml
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


class SPECImplementationReadinessValidator:
    """Validates SPEC files for implementation readiness"""

    ARCHITECTURE_PATTERN = r"architecture:\s*\n\s+overview:|component_structure:|element_ids:|dependencies:"
    INTERFACES_PATTERN = r"interfaces:\s*\n\s+(external_apis:|internal_apis:|classes:)"
    BEHAVIOR_PATTERN = r"behavior:\s*\n\s*-|behavior:\s*\{\{|behavior:" # Flexible behavior format
    PERFORMANCE_PATTERN = r"performance:\s*\n\s+(latency_targets:|throughput_targets:|resource_limits:|caching:)"
    SECURITY_PATTERN = r"security:\s*\n\s+(authentication:|authorization:|encryption:|rate_limiting:)"
    OBSERVABILITY_PATTERN = r"observability:\s*\n\s+(logging:|metrics:|tracing:|alerts:)"
    VERIFICATION_PATTERN = r"verification:\s*\n\s+(unit_tests:|integration_tests:|contract_tests:|performance_tests:)"
    IMPLEMENTATION_PATTERN = r"implementation:\s*\n\s+(configuration:|deployment:|scaling:|dependencies:)"
    REQ_IMPLEMENTATIONS_PATTERN = r"req_implementations:\s*\n\s*-|traceability:.*req_implementations:"
    
    # Concrete examples: pseudocode, algorithms, code snippets
    PSEUDOCODE_PATTERN = r"(pseudocode|algorithm|steps|procedure):|```(python|javascript|java|go|rust|pseudocode)"
    EXAMPLE_PATTERN = r"example|```json|```yaml|payload:|request:|response:|"
    REQUEST_SCHEMA_PATTERN = r"request_schema:|request:|payload:|input:"
    RESPONSE_SCHEMA_PATTERN = r"response_schema:|response:|output:|result:"
    PYDANTIC_PATTERN = r"class\s+\w+\(BaseModel\):|Field\(|Literal\[|Optional\["
    TYPE_ANNOTATION_PATTERN = r"def\s+\w+\([^)]*:\s*\w+|->.*:"

    ERROR_HANDLING_PATTERN = r"error_handling:|error_codes:|exception:|handling:|recovery:"
    STATE_MACHINE_PATTERN = r"state|transition|sm_|fsm|state_machine"

    def __init__(self, min_score: int = 90):
        self.min_score = min_score

    def validate_file(self, file_path: Path) -> ValidationResult:
        result = ValidationResult(file_path=file_path, score=0, passed=False)
        
        if not file_path.exists():
            result.errors.append(f"File not found: {file_path}")
            return result

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                spec_data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            result.errors.append(f"Invalid YAML: {e}")
            return result
        except Exception as e:
            result.errors.append(f"File read error: {e}")
            return result

        if not spec_data or not isinstance(spec_data, dict):
            result.errors.append("YAML is empty or not a dictionary")
            return result

        # Core sections (10 checks × 10 points = 100 points max)
        result.checks["architecture"] = bool(re.search(self.ARCHITECTURE_PATTERN, content, re.IGNORECASE))
        if not result.checks["architecture"]:
            result.warnings.append("Missing or incomplete 'architecture' section")

        result.checks["interfaces"] = bool(re.search(self.INTERFACES_PATTERN, content, re.IGNORECASE))
        if not result.checks["interfaces"]:
            result.warnings.append("Missing or incomplete 'interfaces' section (external_apis, internal_apis, classes)")

        result.checks["behavior"] = bool(re.search(self.BEHAVIOR_PATTERN, content, re.IGNORECASE))
        if not result.checks["behavior"]:
            result.warnings.append("Missing 'behavior' section")

        result.checks["performance"] = bool(re.search(self.PERFORMANCE_PATTERN, content, re.IGNORECASE))
        if not result.checks["performance"]:
            result.warnings.append("Missing performance specifications (latency, throughput, resource limits)")

        result.checks["security"] = bool(re.search(self.SECURITY_PATTERN, content, re.IGNORECASE))
        if not result.checks["security"]:
            result.warnings.append("Missing security specifications (auth, encryption, rate limiting)")

        result.checks["observability"] = bool(re.search(self.OBSERVABILITY_PATTERN, content, re.IGNORECASE))
        if not result.checks["observability"]:
            result.warnings.append("Missing observability specs (logging, metrics, tracing)")

        result.checks["verification"] = bool(re.search(self.VERIFICATION_PATTERN, content, re.IGNORECASE))
        if not result.checks["verification"]:
            result.warnings.append("Missing verification strategy (unit/integration/contract tests)")

        result.checks["implementation"] = bool(re.search(self.IMPLEMENTATION_PATTERN, content, re.IGNORECASE))
        if not result.checks["implementation"]:
            result.warnings.append("Missing implementation details (config, deployment, scaling)")

        result.checks["req_mapping"] = bool(re.search(self.REQ_IMPLEMENTATIONS_PATTERN, content, re.IGNORECASE))
        if not result.checks["req_mapping"]:
            result.warnings.append("Missing REQ-to-implementation mapping (req_implementations)")

        # Quality attributes
        result.checks["concrete_examples"] = self._check_concrete_examples(content, result)
        if not result.checks["concrete_examples"]:
            result.warnings.append("Limited concrete examples (pseudocode, API examples, data models)")

        # Score calculation: 10 points per true check
        result.score = sum(10 for ok in result.checks.values() if ok)
        
        if result.errors:
            result.passed = False
        else:
            result.passed = result.score >= self.min_score

        return result

    def _check_concrete_examples(self, content: str, result: ValidationResult) -> bool:
        """Check for pseudocode, algorithms, code examples, and concrete data"""
        pseudocode_count = len(re.findall(self.PSEUDOCODE_PATTERN, content, re.IGNORECASE))
        example_count = len(re.findall(self.EXAMPLE_PATTERN, content))
        request_count = len(re.findall(self.REQUEST_SCHEMA_PATTERN, content, re.IGNORECASE))
        response_count = len(re.findall(self.RESPONSE_SCHEMA_PATTERN, content, re.IGNORECASE))
        
        total_examples = pseudocode_count + example_count + request_count + response_count
        
        if total_examples < 5:
            result.warnings.append(
                f"Limited concrete examples ({total_examples} found; target: 5+). "
                f"Add pseudocode, API examples, request/response payloads, data models."
            )
            return False
        return True

    def validate_directory(self, directory: Path) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        for f in sorted(directory.rglob("SPEC-*.yaml")):
            if "00_" in f.name or "TEMPLATE" in f.name:
                continue
            results.append(self.validate_file(f))
        return results

    def print_report(self, results: List[ValidationResult]) -> None:
        print("\nSPEC IMPLEMENTATION-READINESS VALIDATION REPORT\n")
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
    parser = argparse.ArgumentParser(description="Validate SPEC files for implementation readiness")
    parser.add_argument("--spec-file", type=Path, help="Path to a SPEC file")
    parser.add_argument("--directory", type=Path, help="Path to SPEC directory")
    parser.add_argument("--min-score", type=int, default=90, help="Minimum score to pass (default: 90)")
    args = parser.parse_args()

    validator = SPECImplementationReadinessValidator(min_score=args.min_score)

    if args.spec_file:
        result = validator.validate_file(args.spec_file)
        validator.print_report([result])
        sys.exit(0 if result.passed else 1)
    elif args.directory:
        results = validator.validate_directory(args.directory)
        validator.print_report(results)
        has_errors = any(r.errors for r in results)
        sys.exit(2 if has_errors else (0 if all(r.passed for r in results) else 1))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
