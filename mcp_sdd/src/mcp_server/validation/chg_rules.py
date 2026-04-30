"""CHG governance validation rules for SDD v3 change records."""

from __future__ import annotations

from typing import Any


_VALID_CHANGE_LEVELS = {"C1", "C2", "C3", "Emergency"}
_VALID_GATES = {"GATE-01", "GATE-03", "GATE-06", "GATE-08", "GATE-CODE"}
_SOURCE_TO_GATE = {
    "upstream": "GATE-01",
    "external": "GATE-01",
    "midstream": "GATE-03",
    "design": "GATE-06",
    "execution": "GATE-08",
    "feedback": "GATE-CODE",
}
_GATE_TO_LAYERS = {
    "GATE-01": {"BRD", "PRD"},
    "GATE-03": {"EARS", "BDD", "ADR"},
    "GATE-06": {"SPEC", "TDD"},
    "GATE-08": {"IPLAN"},
    "GATE-CODE": {"CODE"},
}


def _normalize_layer_name(layer_name: str) -> str:
    text = layer_name.strip().upper()
    if text.startswith("L1") or text == "BRD":
        return "BRD"
    if text.startswith("L2") or text == "PRD":
        return "PRD"
    if text.startswith("L3") or text == "EARS":
        return "EARS"
    if text.startswith("L4") or text == "BDD":
        return "BDD"
    if text.startswith("L5") or text == "ADR":
        return "ADR"
    if text.startswith("L6") or text == "SPEC":
        return "SPEC"
    if text.startswith("L7") or text == "TDD":
        return "TDD"
    if text.startswith("L8") or text == "IPLAN":
        return "IPLAN"
    if "CODE" in text:
        return "CODE"
    return text


def check_change_level(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    change_control = yaml_data.get("change_control", {})
    if not isinstance(change_control, dict):
        errors.append("CHG-001: change_control section missing or invalid")
        return

    level = change_control.get("change_level")
    if not isinstance(level, str) or level not in _VALID_CHANGE_LEVELS:
        errors.append(f"CHG-001: change_level must be one of {_VALID_CHANGE_LEVELS}")
        return

    passes.append(f"CHG-001: change_level valid ({level})")


def check_gate_routing(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    change_control = yaml_data.get("change_control", {})
    if not isinstance(change_control, dict):
        return

    level = str(change_control.get("change_level", "")).strip()
    source = str(change_control.get("change_source", "")).strip().lower()
    entry_gate = change_control.get("entry_gate")

    if level == "C1":
        if entry_gate not in (None, "", "None"):
            errors.append("CHG-002: C1 changes must not specify an entry_gate")
            return
        passes.append("CHG-002: C1 change correctly bypasses formal gates")
        return

    if source in _SOURCE_TO_GATE:
        expected_gate = _SOURCE_TO_GATE[source]
        if entry_gate != expected_gate:
            errors.append(
                f"CHG-002: change_source '{source}' requires entry_gate '{expected_gate}', got '{entry_gate}'"
            )
            return
        passes.append(f"CHG-002: change_source '{source}' correctly routed to {entry_gate}")
        return

    if entry_gate in _VALID_GATES:
        passes.append(f"CHG-002: entry_gate valid ({entry_gate})")
    else:
        errors.append(f"CHG-002: entry_gate must be one of {_VALID_GATES}")


def check_gate_layer_coverage(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    change_control = yaml_data.get("change_control", {})
    impact = yaml_data.get("impact_assessment", {})
    if not isinstance(change_control, dict) or not isinstance(impact, dict):
        return

    gate = change_control.get("entry_gate")
    if not isinstance(gate, str) or gate not in _GATE_TO_LAYERS:
        return

    affected_layers = impact.get("affected_layers", [])
    if not isinstance(affected_layers, list) or not affected_layers:
        warnings.append("CHG-003: impact_assessment.affected_layers missing or empty")
        return

    allowed = _GATE_TO_LAYERS[gate]
    for item in affected_layers:
        if not isinstance(item, dict):
            continue
        raw_layer = item.get("layer")
        if not isinstance(raw_layer, str):
            continue
        normalized = _normalize_layer_name(raw_layer)
        if normalized not in allowed:
            warnings.append(
                f"CHG-003: layer '{raw_layer}' not in typical scope for {gate} ({sorted(allowed)})"
            )

    passes.append(f"CHG-003: gate-layer coverage check applied for {gate}")


def check_gate_approval_requirements(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    change_control = yaml_data.get("change_control", {})
    gate_approval = yaml_data.get("gate_approval", {})
    if not isinstance(change_control, dict):
        return

    level = change_control.get("change_level")
    if level == "C3":
        if not isinstance(gate_approval, dict):
            errors.append("CHG-004: C3 changes require gate_approval section")
            return
        gate = gate_approval.get("gate")
        approver = gate_approval.get("approver")
        if gate not in _VALID_GATES:
            errors.append("CHG-004: C3 changes require valid gate_approval.gate")
            return
        if approver in (None, "", "null"):
            errors.append("CHG-004: C3 changes require gate_approval.approver")
            return
        passes.append("CHG-004: C3 gate approval section is complete")
        return

    if level in {"C1", "C2"}:
        passes.append(f"CHG-004: gate approval not mandatory for {level}")


def check_rollback_and_emergency(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    change_control = yaml_data.get("change_control", {})
    rollback_plan = yaml_data.get("rollback_plan", {})
    emergency_change = yaml_data.get("emergency_change", {})
    if not isinstance(change_control, dict):
        return

    level = change_control.get("change_level")

    if level in {"C2", "C3"}:
        if not isinstance(rollback_plan, dict):
            errors.append(f"CHG-005: {level} changes require rollback_plan section")
        else:
            strategy = rollback_plan.get("strategy")
            if strategy in (None, "", "null"):
                errors.append(f"CHG-005: {level} changes require rollback_plan.strategy")
            else:
                passes.append(f"CHG-005: rollback plan present for {level}")

    if level == "Emergency":
        if not isinstance(emergency_change, dict):
            errors.append("CHG-005: Emergency changes require emergency_change section")
            return
        emergency_id = emergency_change.get("emergency_id")
        fix_deployed = emergency_change.get("fix_deployed")
        post_hoc_gate = emergency_change.get("post_hoc_gate")
        if emergency_id in (None, "", "null"):
            errors.append("CHG-005: Emergency change requires emergency_change.emergency_id")
            return
        if fix_deployed in (None, "", "null"):
            errors.append("CHG-005: Emergency change requires emergency_change.fix_deployed")
            return
        if post_hoc_gate in (None, "", "null"):
            warnings.append("CHG-005: Emergency change should set emergency_change.post_hoc_gate")
        passes.append("CHG-005: emergency change fields validated")


def run_chg_validation_checks(
    *,
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Run CHG governance checks for change records."""
    check_change_level(yaml_data, errors, warnings, passes)
    check_gate_routing(yaml_data, errors, warnings, passes)
    check_gate_layer_coverage(yaml_data, errors, warnings, passes)
    check_gate_approval_requirements(yaml_data, errors, warnings, passes)
    check_rollback_and_emergency(yaml_data, errors, warnings, passes)
