from __future__ import annotations

from dataclasses import dataclass


class ContractConflictError(ValueError):
    """Raised when precedence-selected source conflicts with lower-priority input."""

    def __init__(self, payload: dict[str, object]):
        self.payload = payload
        super().__init__(str(payload))


@dataclass(frozen=True)
class ThresholdResolution:
    threshold_value: float
    threshold_source: str
    formula_source: str
    precedence_trace: tuple[str, ...]


@dataclass(frozen=True)
class ValidationStageResult:
    stage: str
    blocking: bool
    message: str


def resolve_input_source_precedence(sources: dict[str, dict[str, str]]) -> tuple[str, dict[str, str]]:
    for source_name in ("iplan", "ref", "prompt"):
        if source_name in sources:
            return source_name, sources[source_name]
    raise ValueError("No supported source mode provided")


def detect_scope_objective_conflict(sources: dict[str, dict[str, str]]) -> dict[str, object] | None:
    selected_source, selected_payload = resolve_input_source_precedence(sources)
    selected_scope = selected_payload.get("scope", "")
    selected_objective = selected_payload.get("objective", "")

    conflict_fields: list[str] = []
    for source_name in ("iplan", "ref", "prompt"):
        if source_name == selected_source or source_name not in sources:
            continue
        payload = sources[source_name]
        if payload.get("scope", "") and payload.get("scope") != selected_scope:
            conflict_fields.append("scope")
        if payload.get("objective", "") and payload.get("objective") != selected_objective:
            conflict_fields.append("objective")

    if not conflict_fields:
        return None

    return {
        "input_precedence_applied": selected_source,
        "conflict_type": "scope_objective_conflict",
        "conflict_fields": sorted(set(conflict_fields)),
        "blocking_reason": "Conflicting lower-precedence objective/scope directives",
    }


def bind_registry_profile(
    *,
    layer: str,
    profile_name: str,
    profile_metadata: dict[str, object],
    registry: dict[str, dict[str, object]],
    registry_source: str = "framework/registry/LAYER_REGISTRY.yaml",
) -> dict[str, object]:
    if layer not in registry:
        return {
            "registry_source": registry_source,
            "registry_layer_key": layer,
            "registry_binding_status": "missing_layer",
            "registry_drift_fields": ["layer"],
        }

    registry_layer = registry[layer]
    drift_fields: list[str] = []
    for field in ("artifact", "folder", "optional", "required_tags", "can_reference", "template"):
        if field in profile_metadata and profile_metadata[field] != registry_layer.get(field):
            drift_fields.append(field)

    return {
        "profile_name": profile_name,
        "registry_source": registry_source,
        "registry_layer_key": layer,
        "registry_binding_status": "ok" if not drift_fields else "drift",
        "registry_drift_fields": drift_fields,
        "bound_fields": {
            "number": registry_layer.get("number"),
            "artifact": registry_layer.get("artifact"),
            "folder": registry_layer.get("folder"),
            "optional": registry_layer.get("optional"),
            "required_tags": registry_layer.get("required_tags"),
            "can_reference": registry_layer.get("can_reference"),
            "template": registry_layer.get("template"),
            "test_types": registry_layer.get("test_types"),
        },
    }


def resolve_subtype_profile(
    *,
    layer: str,
    subtype_type: str,
    subtype_code: str,
    subtype_catalog: dict[str, dict[str, str]],
    explicit: bool,
) -> dict[str, str]:
    key = f"{subtype_type}:{subtype_code}"
    if key not in subtype_catalog:
        raise ValueError(f"Unsupported subtype: {key}")

    return {
        "layer": layer,
        "subtype_type": subtype_type,
        "subtype_code": subtype_code,
        "subtype_profile": subtype_catalog[key]["profile"],
        "subtype_source": "runtime_input" if explicit else "profile_default",
    }


def run_validation_stages(stages: list[ValidationStageResult]) -> dict[str, object]:
    """Enforce structural-gate-first behavior with deterministic stage order."""

    stage_order = tuple(stage.stage for stage in stages)
    first_blocking = next((stage for stage in stages if stage.blocking), None)
    return {
        "stage_order": stage_order,
        "structural_gate_status": "failed" if first_blocking and first_blocking.stage == "structure" else "passed",
        "first_blocking_stage": first_blocking.stage if first_blocking else None,
        "blocked_message": first_blocking.message if first_blocking else None,
    }


def enforce_layer_boundary(
    *,
    source_layer: str,
    text: str,
    forbidden_patterns: dict[str, str],
) -> dict[str, object] | None:
    lowered = text.casefold()
    for target_layer, pattern in forbidden_patterns.items():
        if pattern.casefold() in lowered:
            return {
                "boundary_rule": "forbidden_downstream_syntax",
                "offending_pattern": pattern,
                "target_layer": target_layer,
                "source_layer": source_layer,
            }
    return None


def resolve_threshold_precedence(
    *,
    explicit_threshold: float | None,
    profile_threshold: float | None,
    registry_threshold: float | None,
    default_threshold: float,
    explicit_formula: str | None,
    profile_formula: str | None,
    registry_formula: str | None,
    default_formula: str,
) -> ThresholdResolution:
    precedence_trace: list[str] = []

    if explicit_threshold is not None:
        threshold = explicit_threshold
        threshold_source = "runtime_profile"
    elif profile_threshold is not None:
        threshold = profile_threshold
        threshold_source = "profile"
    elif registry_threshold is not None:
        threshold = registry_threshold
        threshold_source = "registry"
    else:
        threshold = default_threshold
        threshold_source = "default"
    precedence_trace.append(f"threshold:{threshold_source}")

    if explicit_formula is not None:
        formula_source = "runtime_profile"
    elif profile_formula is not None:
        formula_source = "profile"
    elif registry_formula is not None:
        formula_source = "registry"
    else:
        formula_source = "default"
    precedence_trace.append(f"formula:{formula_source}")

    return ThresholdResolution(
        threshold_value=threshold,
        threshold_source=threshold_source,
        formula_source=formula_source,
        precedence_trace=tuple(precedence_trace),
    )
