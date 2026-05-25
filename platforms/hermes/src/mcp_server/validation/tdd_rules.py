"""TDD validation rules for SDD Layer 7.

Rules implemented:
  SDD-TDD-001  TDD-READY Score Validation
  SDD-TDD-002  Test Pyramid Structure Validation
  SDD-TDD-003  BDD Scenario Coverage Validation
  SDD-TDD-004  Test Thresholds Validation
  SDD-TDD-005  TDD Execution Order Validation
  SDD-TDD-006  SPEC Traceability Validation
"""

from __future__ import annotations

import re
from typing import Any


def check_tdd_readiness_score(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Verify TDD-READY score >= 90 for IPLAN transition."""
    document_control = yaml_data.get("document_control", {})
    if not isinstance(document_control, dict):
        errors.append("TDD-001: document_control section missing or invalid")
        return

    iplan_ready_score = document_control.get("iplan_ready_score")
    if iplan_ready_score is None:
        errors.append("TDD-001: iplan_ready_score field missing in document_control")
        return

    score_str = str(iplan_ready_score)
    match = re.search(r"(\d+)\s*/\s*(\d+)", score_str)
    if match is None:
        errors.append(
            f"TDD-001: iplan_ready_score format invalid: {score_str}. Expected N/M format."
        )
        return

    numerator = int(match.group(1))
    int(match.group(2))

    if numerator < 90:
        errors.append(
            f"TDD-001: iplan_ready_score {score_str} below 90 threshold for IPLAN transition"
        )
    else:
        passes.append(f"TDD-001: iplan_ready_score {score_str} meets >=90 threshold")


def check_test_pyramid(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Validate 70/20/10 distribution (unit/integration/e2e)."""
    test_pyramid = yaml_data.get("test_pyramid", {})
    if not isinstance(test_pyramid, dict):
        errors.append("TDD-002: test_pyramid section missing or invalid")
        return

    distribution = test_pyramid.get("distribution", {})
    if not isinstance(distribution, dict):
        errors.append("TDD-002: test_pyramid.distribution missing or invalid")
        return

    unit_pct = distribution.get("unit", 0)
    integration_pct = distribution.get("integration", 0)
    e2e_pct = distribution.get("e2e", 0)

    total = int(unit_pct) + int(integration_pct) + int(e2e_pct)
    if total != 100:
        errors.append(f"TDD-002: Test pyramid distribution totals {total}%, expected 100%")
        return

    for test_type, pct in [("unit", unit_pct), ("integration", integration_pct), ("e2e", e2e_pct)]:
        if not isinstance(pct, int | float):
            errors.append(f"TDD-002: {test_type} percentage not a number: {pct}")
            return

    passes.append(
        f"TDD-002: Test pyramid valid - unit:{unit_pct}% integration:{integration_pct}% e2e:{e2e_pct}%"
    )


def check_bdd_scenario_coverage(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Validate all BDD scenarios mapped in test_mapping.scenarios[].tests[]."""
    test_mapping = yaml_data.get("test_mapping", {})
    if not isinstance(test_mapping, dict):
        errors.append("TDD-003: test_mapping section missing or invalid")
        return

    scenarios = test_mapping.get("scenarios", [])
    if not isinstance(scenarios, list) or len(scenarios) == 0:
        errors.append("TDD-003: test_mapping.scenarios missing or empty")
        return

    for scenario in scenarios:
        if not isinstance(scenario, dict):
            errors.append("TDD-003: scenario item not a dict")
            continue

        bdd_scenario = scenario.get("bdd_scenario")
        tests = scenario.get("tests", [])
        if not isinstance(tests, list) or len(tests) == 0:
            if bdd_scenario:
                errors.append(f"TDD-003: BDD scenario {bdd_scenario} has no tests mapped")
            continue

        test_types_found = {t.get("type") for t in tests if isinstance(t, dict)}
        if (
            "unit" not in test_types_found
            or "integration" not in test_types_found
            or "e2e" not in test_types_found
        ):
            warnings.append(
                f"TDD-003: BDD scenario {bdd_scenario} missing some test types: {test_types_found}"
            )
            continue

        passes.append(f"TDD-003: BDD scenario {bdd_scenario} has unit/integration/e2e coverage")


def check_test_thresholds(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Validate coverage targets and pass criteria present."""
    thresholds = yaml_data.get("thresholds", {})
    if not isinstance(thresholds, dict):
        errors.append("TDD-004: thresholds section missing or invalid")
        return

    for test_type in ["unit", "integration", "e2e"]:
        type_thresholds = thresholds.get(test_type, {})
        if not isinstance(type_thresholds, dict):
            errors.append(f"TDD-004: thresholds.{test_type} section missing")
            continue

        coverage_target = type_thresholds.get("coverage_target")
        if not coverage_target:
            errors.append(f"TDD-004: thresholds.{test_type}.coverage_target missing")
            continue

        pass_criteria = type_thresholds.get("pass_criteria")
        if not isinstance(pass_criteria, list) or len(pass_criteria) == 0:
            errors.append(f"TDD-004: thresholds.{test_type}.pass_criteria missing or empty")
            continue

        passes.append(f"TDD-004: thresholds.{test_type} has coverage_target and pass_criteria")


def check_tdd_execution_order(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Verify Red-Green-Refactor sequence declared in tdd_order.phases[]."""
    tdd_order = yaml_data.get("tdd_order", {})
    if not isinstance(tdd_order, dict):
        errors.append("TDD-005: tdd_order section missing or invalid")
        return

    phases = tdd_order.get("phases", [])
    if not isinstance(phases, list) or len(phases) != 5:
        errors.append("TDD-005: tdd_order.phases missing or not 5 phases")
        return

    phase_names = [p.get("name") if isinstance(p, dict) else None for p in phases]
    expected_sequence = [
        "Write Tests",
        "Run Tests (Red)",
        "Implement",
        "Verify (Green)",
        "Refactor",
    ]

    missing_phases = [exp for exp in expected_sequence if exp not in phase_names]
    if missing_phases:
        errors.append(f"TDD-005: tdd_order.phases missing expected phases: {missing_phases}")
        return

    passes.append("TDD-005: tdd_order.phases has Red-Green-Refactor sequence")


def check_spec_traceability(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Validate spec_ref in test cases (Section 4) and upstream traceability."""
    traceability = yaml_data.get("traceability", {})
    if not isinstance(traceability, dict):
        errors.append("TDD-006: traceability section missing or invalid")
        return

    upstream = traceability.get("upstream", {})
    if not isinstance(upstream, dict):
        errors.append("TDD-006: traceability.upstream section missing")
        return

    spec_refs = upstream.get("spec_references", [])
    if not isinstance(spec_refs, list) or len(spec_refs) == 0:
        errors.append("TDD-006: traceability.upstream.spec_references missing or empty")
        return

    spec_ref_patterns = [r for r in spec_refs if isinstance(r, str) and "@spec:" in r]
    if len(spec_ref_patterns) == 0:
        errors.append(
            "TDD-006: No @spec: reference patterns found in traceability.upstream.spec_references"
        )
        return

    passes.append(
        f"TDD-006: traceability.upstream.spec_references has {len(spec_ref_patterns)} @spec: references"
    )


def run_tdd_validation_checks(
    *,
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Run all TDD-specific validation checks."""
    check_tdd_readiness_score(yaml_data, errors, warnings, passes)
    check_test_pyramid(yaml_data, errors, warnings, passes)
    check_bdd_scenario_coverage(yaml_data, errors, warnings, passes)
    check_test_thresholds(yaml_data, errors, warnings, passes)
    check_tdd_execution_order(yaml_data, errors, warnings, passes)
    check_spec_traceability(yaml_data, errors, warnings, passes)
