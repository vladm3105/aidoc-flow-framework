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
    """Validates SPEC files for implementation readiness (schema-aware)"""

    # Legacy regexes kept for example counting and permissive fallback detection
    PSEUDOCODE_PATTERN = r"(pseudocode|algorithm|steps|procedure):|```(python|javascript|java|go|rust|pseudocode)"
    EXAMPLE_PATTERN = r"example|```json|```yaml|payload:|request:|response:|"
    REQUEST_SCHEMA_PATTERN = r"request_schema:|request:|payload:|input:"
    RESPONSE_SCHEMA_PATTERN = r"response_schema:|response:|output:|result:"
    PYDANTIC_PATTERN = r"class\s+\w+\(BaseModel\):|Field\(|Literal\[|Optional\["
    TYPE_ANNOTATION_PATTERN = r"def\s+\w+\([^)]*:\s*\w+|->.*:"

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
        result.checks["architecture"] = self._has_architecture(spec_data)
        if not result.checks["architecture"]:
            result.warnings.append("Missing or incomplete 'architecture' (overview/component_structure/element_ids)")

        result.checks["interfaces"] = self._has_interfaces(spec_data)
        if not result.checks["interfaces"]:
            result.warnings.append("Missing 'interfaces' (need external_apis/internal_apis/classes)")

        result.checks["behavior"] = self._has_behavior(spec_data)
        if not result.checks["behavior"]:
            result.warnings.append("Missing 'behavior' section with pseudocode/steps")

        result.checks["performance"] = self._has_performance(spec_data)
        if not result.checks["performance"]:
            result.warnings.append("Missing performance targets (latency/throughput/resource_limits)")

        result.checks["security"] = self._has_security(spec_data)
        if not result.checks["security"]:
            result.warnings.append("Missing security specifications (authN/Z, encryption, rate limits/redaction)")

        result.checks["observability"] = self._has_observability(spec_data)
        if not result.checks["observability"]:
            result.warnings.append("Missing observability (logging/metrics/tracing/alerting)")

        result.checks["verification"] = self._has_verification(spec_data)
        if not result.checks["verification"]:
            result.warnings.append("Missing verification strategy (unit+integration at minimum)")

        result.checks["implementation"] = self._has_implementation(spec_data)
        if not result.checks["implementation"]:
            result.warnings.append("Missing implementation details (config/env/deployment/scaling)")

        result.checks["req_mapping"] = self._has_req_mapping(spec_data, result)
        if not result.checks["req_mapping"]:
            result.warnings.append("REQ mapping incomplete (requires req_implementations with test_approach)")

        # Quality attributes
        result.checks["concrete_examples"] = self._check_concrete_examples(content, result, spec_data)
        if not result.checks["concrete_examples"]:
            result.warnings.append("Limited concrete examples (pseudocode, API examples, pydantic models)")

        # Score calculation: 10 points per true check
        result.score = sum(10 for ok in result.checks.values() if ok)
        
        if result.errors:
            result.passed = False
        else:
            result.passed = result.score >= self.min_score

        return result

    # --- semantic checks ---
    def _has_architecture(self, spec: dict) -> bool:
        section = spec.get("architecture", {})
        return bool(section and isinstance(section, dict) and any(section.get(k) for k in ["overview", "component_structure", "element_ids"]))

    def _has_interfaces(self, spec: dict) -> bool:
        interfaces = spec.get("interfaces", {})
        if not isinstance(interfaces, dict):
            return False
        return any(interfaces.get(k) for k in ["external_apis", "internal_apis", "classes"])

    def _has_behavior(self, spec: dict) -> bool:
        behavior = spec.get("behavior")
        return bool(behavior)

    def _has_performance(self, spec: dict) -> bool:
        perf = spec.get("performance", {})
        if not isinstance(perf, dict):
            return False
        return any(perf.get(k) for k in ["latency_targets", "throughput_targets", "resource_limits", "caching"])

    def _has_security(self, spec: dict) -> bool:
        sec = spec.get("security", {})
        if not isinstance(sec, dict):
            return False
        return any(sec.get(k) for k in ["authentication", "authorization", "encryption", "rate_limiting", "redaction", "immutability"])

    def _has_observability(self, spec: dict) -> bool:
        obs = spec.get("observability", {})
        if not isinstance(obs, dict):
            return False
        return any(obs.get(k) for k in ["logging", "metrics", "tracing", "alerting", "alerts"])

    def _has_verification(self, spec: dict) -> bool:
        ver = spec.get("verification", {})
        if not isinstance(ver, dict):
            return False
        has_unit = "unit_tests" in ver
        has_integration = "integration_tests" in ver
        return has_unit and has_integration

    def _has_implementation(self, spec: dict) -> bool:
        impl = spec.get("implementation", {})
        if not isinstance(impl, dict):
            return False
        return any(impl.get(k) for k in ["configuration", "configuration_files", "environment_variables", "deployment", "scaling", "autoscaling"])

    def _has_req_mapping(self, spec: dict, result: ValidationResult) -> bool:
        reqs = spec.get("req_implementations")
        if not reqs or not isinstance(reqs, list):
            result.warnings.append("req_implementations missing or empty")
            return False

        missing = []
        for idx, req in enumerate(reqs, start=1):
            req_id = req.get("req_id") or f"REQ?#{idx}"
            impl = req.get("implementation")
            test_approach = req.get("test_approach")
            if not impl:
                missing.append(f"{req_id}: implementation block missing")
            if not test_approach:
                missing.append(f"{req_id}: test_approach missing (unit+integration required)")
                continue
            if not isinstance(test_approach, dict):
                missing.append(f"{req_id}: test_approach should be a mapping")
                continue
            unit_cases = test_approach.get("unit_tests") or []
            int_cases = test_approach.get("integration_tests") or []
            if len(unit_cases) == 0:
                missing.append(f"{req_id}: unit_tests empty")
            if len(int_cases) == 0:
                missing.append(f"{req_id}: integration_tests empty")

        if missing:
            result.warnings.extend([f"REQ mapping issue: {m}" for m in missing])
            return False
        return True

    def _check_concrete_examples(self, content: str, result: ValidationResult, spec: dict) -> bool:
        """Check for pseudocode, algorithms, code examples, and concrete data"""
        pseudocode_count = len(re.findall(self.PSEUDOCODE_PATTERN, content, re.IGNORECASE))
        example_count = len(re.findall(self.EXAMPLE_PATTERN, content))
        request_count = len(re.findall(self.REQUEST_SCHEMA_PATTERN, content, re.IGNORECASE))
        response_count = len(re.findall(self.RESPONSE_SCHEMA_PATTERN, content, re.IGNORECASE))

        yaml_based = 0
        if spec.get("pydantic_models"):
            yaml_based += 1
        if spec.get("behavioral_examples"):
            yaml_based += 1
        interfaces = spec.get("interfaces", {})
        if isinstance(interfaces, dict) and interfaces.get("external_apis"):
            yaml_based += 1

        total_examples = pseudocode_count + example_count + request_count + response_count + yaml_based

        if total_examples < 5:
            result.warnings.append(
                f"Limited concrete examples ({total_examples} found; target: 5+). "
                f"Add pseudocode, API examples, request/response payloads, pydantic models."
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
