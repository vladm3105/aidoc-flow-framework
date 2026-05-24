from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.validation.tdd_rules import run_tdd_validation_checks  # noqa: E402


def test_tdd_rules_pass_with_minimal_valid_payload() -> None:
    yaml_data = {
        "document_control": {"iplan_ready_score": "90/100"},
        "test_pyramid": {"distribution": {"unit": 70, "integration": 20, "e2e": 10}},
        "test_mapping": {
            "scenarios": [
                {
                    "bdd_scenario": "@bdd: BDD.01.abcd",
                    "tests": [
                        {"type": "unit"},
                        {"type": "integration"},
                        {"type": "e2e"},
                    ],
                }
            ]
        },
        "thresholds": {
            "unit": {"coverage_target": ">=90%", "pass_criteria": ["All pass"]},
            "integration": {"coverage_target": ">=85%", "pass_criteria": ["All pass"]},
            "e2e": {"coverage_target": ">=75%", "pass_criteria": ["All pass"]},
        },
        "tdd_order": {
            "phases": [
                {"name": "Write Tests"},
                {"name": "Run Tests (Red)"},
                {"name": "Implement"},
                {"name": "Verify (Green)"},
                {"name": "Refactor"},
            ]
        },
        "traceability": {"upstream": {"spec_references": ["@spec: SPEC-01"]}},
    }
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_tdd_validation_checks(yaml_data=yaml_data, errors=errors, warnings=warnings, passes=passes)
    assert not errors
    assert any(msg.startswith("TDD-001") for msg in passes)


def test_tdd_rules_fail_when_readiness_below_threshold() -> None:
    yaml_data = {
        "document_control": {"iplan_ready_score": "89/100"},
        "test_pyramid": {"distribution": {"unit": 70, "integration": 20, "e2e": 10}},
        "test_mapping": {
            "scenarios": [{"bdd_scenario": "@bdd: BDD.01.abcd", "tests": [{"type": "unit"}]}]
        },
        "thresholds": {
            "unit": {"coverage_target": ">=90%", "pass_criteria": ["All pass"]},
            "integration": {"coverage_target": ">=85%", "pass_criteria": ["All pass"]},
            "e2e": {"coverage_target": ">=75%", "pass_criteria": ["All pass"]},
        },
        "tdd_order": {"phases": [{"name": "Write Tests"}]},
        "traceability": {"upstream": {"spec_references": ["@spec: SPEC-01"]}},
    }
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_tdd_validation_checks(yaml_data=yaml_data, errors=errors, warnings=warnings, passes=passes)
    assert any(msg.startswith("TDD-001") for msg in errors)
