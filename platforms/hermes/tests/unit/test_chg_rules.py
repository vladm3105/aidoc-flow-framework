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


def _base_spec_chg_payload() -> dict[str, object]:
    """A valid C2 framework-spec change routed to GATE-SPEC."""
    return {
        "change_control": {
            "change_level": "C2",
            "change_source": "spec",
            "entry_gate": "GATE-SPEC",
            "semver_impact": "minor",
        },
        "change_description": {
            "why": "close a registry gap shared by both platforms",
            "trigger": "learnings LRN-03 recurred across 3 projects",
        },
        "impact_assessment": {
            "affected_layers": [{"layer": "framework", "artifacts": ["LAYER_REGISTRY"]}]
        },
        "rollback_plan": {"strategy": "revert-commit", "steps": ["revert"]},
    }


def _run(yaml_data: dict[str, object]) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_chg_validation_checks(yaml_data=yaml_data, errors=errors, warnings=warnings, passes=passes)
    return errors, warnings, passes


def test_spec_source_routes_to_gate_spec_and_passes() -> None:
    errors, _, passes = _run(_base_spec_chg_payload())
    assert not errors
    assert any("spec '" in msg or "spec" in msg for msg in passes)
    assert any(msg.startswith("CHG-002") for msg in passes)


def test_spec_change_rejects_c1() -> None:
    yaml_data = _base_spec_chg_payload()
    yaml_data["change_control"]["change_level"] = "C1"  # type: ignore[index]
    yaml_data["change_control"]["entry_gate"] = None     # type: ignore[index]
    errors, _, _ = _run(yaml_data)
    assert any("GATE-SPEC-E003" in msg for msg in errors)


def test_spec_change_requires_semver_impact() -> None:
    yaml_data = _base_spec_chg_payload()
    del yaml_data["change_control"]["semver_impact"]  # type: ignore[union-attr]
    errors, _, _ = _run(yaml_data)
    assert any("GATE-SPEC-E002" in msg for msg in errors)


def test_spec_change_major_must_be_c3() -> None:
    yaml_data = _base_spec_chg_payload()
    yaml_data["change_control"]["semver_impact"] = "major"  # type: ignore[index]
    errors, _, _ = _run(yaml_data)
    assert any("GATE-SPEC-E002" in msg for msg in errors)


def test_spec_change_requires_provenance() -> None:
    yaml_data = _base_spec_chg_payload()
    yaml_data["change_description"] = {"why": "", "trigger": ""}
    errors, _, _ = _run(yaml_data)
    assert any("GATE-SPEC-E001" in msg for msg in errors)
