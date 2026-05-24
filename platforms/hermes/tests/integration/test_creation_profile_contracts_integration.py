from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.creation.profile_contracts import (  # noqa: E402
    ContractConflictError,
    ValidationStageResult,
    bind_registry_profile,
    detect_scope_objective_conflict,
    enforce_layer_boundary,
    resolve_subtype_profile,
    resolve_threshold_precedence,
    run_validation_stages,
)


def _validate_creation_contract_payload(sources: dict[str, dict[str, str]]) -> dict[str, object]:
    conflict = detect_scope_objective_conflict(sources)
    if conflict:
        raise ContractConflictError(conflict)
    return {"status": "ok"}


def test_conflicting_scope_or_objective_between_sources_returns_explicit_failure() -> None:
    try:
        _validate_creation_contract_payload(
            {
                "iplan": {"scope": "A", "objective": "X"},
                "ref": {"scope": "B", "objective": "X"},
            }
        )
    except ContractConflictError as exc:
        payload = exc.payload
        assert payload["input_precedence_applied"] == "iplan"
        assert "scope" in payload["conflict_fields"]
        assert payload["blocking_reason"]
    else:
        raise AssertionError("Expected ContractConflictError")


def test_validate_uses_active_registry_metadata_for_target_artifact() -> None:
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
    assert result["registry_source"] == "framework/registry/LAYER_REGISTRY.yaml"


def test_subtype_code_routes_to_expected_subtype_profile_end_to_end() -> None:
    resolved = resolve_subtype_profile(
        layer="spec",
        subtype_type="deliverable",
        subtype_code="cspec",
        subtype_catalog={"deliverable:cspec": {"profile": "spec-cspec"}},
        explicit=True,
    )
    assert resolved["subtype_profile"] == "spec-cspec"
    assert resolved["subtype_source"] == "runtime_input"


def test_validate_stops_on_blocking_structure_violation_before_content_checks() -> None:
    result = run_validation_stages(
        [
            ValidationStageResult(stage="structure", blocking=True, message="folder missing"),
            ValidationStageResult(stage="content", blocking=True, message="bad section"),
        ]
    )
    assert result["first_blocking_stage"] == "structure"
    assert result["blocked_message"] == "folder missing"


def test_cross_layer_reference_violation_fails_validation_with_boundary_error() -> None:
    violation = enforce_layer_boundary(
        source_layer="prd",
        text="Then system shall call API",
        forbidden_patterns={"bdd": "Then"},
    )
    assert violation is not None
    assert violation["boundary_rule"] == "forbidden_downstream_syntax"
    assert violation["source_layer"] == "prd"


def test_scoring_conflict_uses_active_precedence_source_consistently() -> None:
    first = resolve_threshold_precedence(
        explicit_threshold=0.95,
        profile_threshold=0.9,
        registry_threshold=0.85,
        default_threshold=0.8,
        explicit_formula="runtime-v3",
        profile_formula="profile-v2",
        registry_formula="registry-v1",
        default_formula="default-v1",
    )
    second = resolve_threshold_precedence(
        explicit_threshold=0.95,
        profile_threshold=0.9,
        registry_threshold=0.85,
        default_threshold=0.8,
        explicit_formula="runtime-v3",
        profile_formula="profile-v2",
        registry_formula="registry-v1",
        default_formula="default-v1",
    )
    assert first == second
    assert first.threshold_source == "runtime_profile"
    assert first.formula_source == "runtime_profile"
