from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.creation import (  # noqa: E402
    ValidationStageResult,
    bind_registry_profile,
    enforce_layer_boundary,
    resolve_input_source_precedence,
    resolve_subtype_profile,
    resolve_threshold_precedence,
    run_validation_stages,
)


def test_input_source_precedence_iplan_over_ref_over_prompt() -> None:
    source_name, payload = resolve_input_source_precedence(
        {
            "prompt": {"scope": "prompt"},
            "ref": {"scope": "ref"},
            "iplan": {"scope": "iplan"},
        }
    )
    assert source_name == "iplan"
    assert payload["scope"] == "iplan"


def test_profile_binding_matches_authoritative_registry_entry() -> None:
    result = bind_registry_profile(
        layer="spec",
        profile_name="spec-default",
        profile_metadata={"artifact": "spec", "folder": "09_SPEC", "optional": False},
        registry={
            "spec": {
                "number": 9,
                "artifact": "spec",
                "folder": "09_SPEC",
                "optional": False,
                "required_tags": ["layer-9-artifact"],
                "can_reference": ["req", "ctr"],
                "template": "SPEC-MVP-TEMPLATE.md",
            }
        },
    )
    assert result["registry_binding_status"] == "ok"
    assert result["registry_drift_fields"] == []


def test_subtype_profile_resolution_is_deterministic() -> None:
    catalog = {"deliverable:cspec": {"profile": "spec-cspec"}}
    first = resolve_subtype_profile(
        layer="spec",
        subtype_type="deliverable",
        subtype_code="cspec",
        subtype_catalog=catalog,
        explicit=True,
    )
    second = resolve_subtype_profile(
        layer="spec",
        subtype_type="deliverable",
        subtype_code="cspec",
        subtype_catalog=catalog,
        explicit=True,
    )
    assert first == second


def test_folder_structure_gate_runs_before_non_structural_checks() -> None:
    result = run_validation_stages(
        [
            ValidationStageResult(stage="structure", blocking=True, message="missing folder"),
            ValidationStageResult(stage="content", blocking=False, message="ok"),
        ]
    )
    assert result["first_blocking_stage"] == "structure"
    assert result["structural_gate_status"] == "failed"


def test_boundary_patterns_reject_downstream_syntax_in_layer() -> None:
    violation = enforce_layer_boundary(
        source_layer="prd",
        text="Given a user opens the page",
        forbidden_patterns={"bdd": "Given"},
    )
    assert violation is not None
    assert violation["source_layer"] == "prd"
    assert violation["target_layer"] == "bdd"


def test_threshold_precedence_order_profile_then_registry_then_defaults() -> None:
    result = resolve_threshold_precedence(
        explicit_threshold=None,
        profile_threshold=0.9,
        registry_threshold=0.85,
        default_threshold=0.8,
        explicit_formula=None,
        profile_formula="profile-v2",
        registry_formula="registry-v1",
        default_formula="default-v1",
    )
    assert result.threshold_value == 0.9
    assert result.threshold_source == "profile"
    assert result.formula_source == "profile"
