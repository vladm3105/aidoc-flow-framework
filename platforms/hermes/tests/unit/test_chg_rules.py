from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.validation.chg_rules import run_chg_validation_checks  # noqa: E402


def _base_chg_payload() -> dict[str, object]:
    return {
        "change_control": {
            "change_level": "C3",
            "change_source": "design",
            "entry_gate": "GATE-06",
        },
        "impact_assessment": {
            "affected_layers": [
                {"layer": "SPEC", "artifacts": ["SPEC-01"]},
                {"layer": "TDD", "artifacts": ["TDD-01"]},
            ]
        },
        "gate_approval": {
            "gate": "GATE-06",
            "approver": "architect",
        },
        "rollback_plan": {
            "strategy": "revert-commit",
            "steps": ["revert"],
        },
        "emergency_change": {
            "emergency_id": None,
            "fix_deployed": None,
            "post_hoc_gate": None,
        },
    }


def test_chg_rules_pass_for_valid_c3_design_change() -> None:
    yaml_data = _base_chg_payload()
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_chg_validation_checks(yaml_data=yaml_data, errors=errors, warnings=warnings, passes=passes)
    assert not errors
    assert any(msg.startswith("CHG-001") for msg in passes)
    assert any(msg.startswith("CHG-004") for msg in passes)


def test_chg_rules_fail_when_source_gate_mismatch() -> None:
    yaml_data = _base_chg_payload()
    change_control = yaml_data["change_control"]
    assert isinstance(change_control, dict)
    change_control["entry_gate"] = "GATE-03"
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_chg_validation_checks(yaml_data=yaml_data, errors=errors, warnings=warnings, passes=passes)
    assert any(msg.startswith("CHG-002") for msg in errors)


def test_chg_rules_require_emergency_fields() -> None:
    yaml_data = _base_chg_payload()
    change_control = yaml_data["change_control"]
    assert isinstance(change_control, dict)
    change_control["change_level"] = "Emergency"
    change_control["entry_gate"] = "GATE-CODE"
    change_control["change_source"] = "feedback"
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_chg_validation_checks(yaml_data=yaml_data, errors=errors, warnings=warnings, passes=passes)
    assert any(msg.startswith("CHG-005") for msg in errors)
