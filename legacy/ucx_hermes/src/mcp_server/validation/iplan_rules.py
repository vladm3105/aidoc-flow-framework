"""IPLAN validation rules for SDD Layer 8.

Rules implemented:
  SDD-IPLAN-001  IPLAN-READY Score Validation
  SDD-IPLAN-002  File Manifest Validation
  SDD-IPLAN-003  Execution Commands Validation
  SDD-IPLAN-004  Session Handoff Protocol Validation
  SDD-IPLAN-005  TDD/Spec Traceability Validation
  SDD-IPLAN-006  Implementation Contracts Validation (optional)
"""

from __future__ import annotations

import re
from typing import Any


def check_iplan_readiness_score(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Verify IPLAN-READY score >= 90 for Code transition."""
    document_control = yaml_data.get("document_control", {})
    if not isinstance(document_control, dict):
        errors.append("IPLAN-001: document_control section missing or invalid")
        return

    iplan_ready_score = document_control.get("iplan_ready_score")
    if iplan_ready_score is None:
        errors.append("IPLAN-001: iplan_ready_score field missing in document_control")
        return

    score_str = str(iplan_ready_score)
    match = re.search(r"(\d+)\s*/\s*(\d+)", score_str)
    if match is None:
        errors.append(
            f"IPLAN-001: iplan_ready_score format invalid: {score_str}. Expected N/M format."
        )
        return

    numerator = int(match.group(1))
    denominator = int(match.group(2))

    if numerator < 90:
        errors.append(
            f"IPLAN-001: iplan_ready_score {score_str} below 90 threshold for Code transition"
        )
    else:
        passes.append(f"IPLAN-001: iplan_ready_score {score_str} meets >=90 threshold")


def check_file_manifest(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Validate file_manifest.files structure with required fields."""
    file_manifest = yaml_data.get("file_manifest", {})
    if not isinstance(file_manifest, dict):
        errors.append("IPLAN-002: file_manifest section missing or invalid")
        return

    files = file_manifest.get("files", [])
    if not isinstance(files, list) or len(files) == 0:
        errors.append("IPLAN-002: file_manifest.files missing or empty")
        return

    required_fields = ["path", "order", "status", "session", "verified"]
    status_values = {"NOT_STARTED", "IN_PROGRESS", "DONE", "PARTIAL"}

    for file_info in files:
        if not isinstance(file_info, dict):
            errors.append("IPLAN-002: file item not a dict")
            continue

        missing_fields = [f for f in required_fields if f not in file_info]
        if missing_fields:
            errors.append(
                f"IPLAN-002: file_manifest.files item missing fields: {missing_fields}"
            )
            continue

        if file_info.get("status") not in status_values:
            errors.append(
                f"IPLAN-002: file_manifest.files status Invalid: {file_info.get('status')}"
            )
            continue

    passes.append(f"IPLAN-002: file_manifest.files has {len(files)} files with valid structure")


def check_execution_commands(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Verify setup, implementation, and validation commands present."""
    execution_commands = yaml_data.get("execution_commands", {})
    if not isinstance(execution_commands, dict):
        errors.append("IPLAN-003: execution_commands section missing or invalid")
        return

    required_categories = ["setup", "implementation", "validation"]
    for category in required_categories:
        commands = execution_commands.get(category)
        if not isinstance(commands, list) or len(commands) == 0:
            errors.append(f"IPLAN-003: execution_commands.{category} missing or empty")
            continue

        pass_str = f"IPLAN-003: execution_commands.{category} has {len(commands)} commands"
        if pass_str not in passes:
            passes.append(pass_str)


def check_session_handoff(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Validate session_handoff structure with markers."""
    session_handoff = yaml_data.get("session_handoff", {})
    if not isinstance(session_handoff, dict):
        errors.append("IPLAN-004: session_handoff section missing or invalid")
        return

    sessions = session_handoff.get("sessions", [])
    if not isinstance(sessions, list):
        errors.append("IPLAN-004: session_handoff.sessions not a list")
        return

    markers = {"NOT_STARTED", "IN_PROGRESS", "DONE", "PARTIAL"}
    for session in sessions:
        if not isinstance(session, dict):
            continue

        files_touched = session.get("files_touched", [])
        if not isinstance(files_touched, list):
            continue

        for ft in files_touched:
            if not isinstance(ft, dict):
                continue
            status = ft.get("status")
            if status and status not in markers:
                errors.append(f"IPLAN-004: Invalid session handoff marker: {status}")
                return

    passes.append(f"IPLAN-004: session_handoff.sessions initialized with {len(sessions)} sessions")


def check_tdd_traceability(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Verify tdd_ref and spec_ref links present in traceability."""
    traceability = yaml_data.get("traceability", {})
    if not isinstance(traceability, dict):
        errors.append("IPLAN-005: traceability section missing or invalid")
        return

    upstream = traceability.get("upstream", {})
    if not isinstance(upstream, dict):
        errors.append("IPLAN-005: traceability.upstream section missing")
        return

    spec_refs = upstream.get("spec_references", [])
    tdd_refs = upstream.get("tdd_references", [])

    if not isinstance(spec_refs, list) or len(spec_refs) == 0:
        errors.append("IPLAN-005: traceability.upstream.spec_references missing or empty")
        return

    if not isinstance(tdd_refs, list) or len(tdd_refs) == 0:
        errors.append("IPLAN-005: traceability.upstream.tdd_references missing or empty")
        return

    spec_ref_patterns = [r for r in spec_refs if isinstance(r, str) and "@spec:" in r]
    tdd_ref_patterns = [r for r in tdd_refs if isinstance(r, str) and "@tdd:" in r]

    if len(spec_ref_patterns) == 0:
        errors.append("IPLAN-005: No @spec: reference patterns found")
        return

    if len(tdd_ref_patterns) == 0:
        errors.append("IPLAN-005: No @tdd: reference patterns found")
        return

    passes.append(
        f"IPLAN-005: traceability has {len(spec_ref_patterns)} @spec: and {len(tdd_ref_patterns)} @tdd: references"
    )


def check_implementation_contracts(
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Optional: Validate implementation contracts if present."""
    implementation_contracts = yaml_data.get("implementation_contracts", {})
    if not isinstance(implementation_contracts, dict):
        passes.append("IPLAN-006: No implementation_contracts section (optional)")
        return

    provided = implementation_contracts.get("provided", {})
    if not isinstance(provided, dict):
        errors.append("IPLAN-006: implementation_contracts.provided invalid")
        return

    contracts = provided.get("contracts", [])
    if not isinstance(contracts, list):
        errors.append("IPLAN-006: implementation_contracts.provided.contracts not a list")
        return

    file_manifest = yaml_data.get("file_manifest", {})
    files = file_manifest.get("files", [])
    file_count = len([f for f in files if isinstance(f, dict)])

    if len(contracts) > 0 and file_count < 3:
        errors.append(
            "IPLAN-006: Implementation contracts present but file_count < 3. Consider removing contracts."
        )
        return

    if len(contracts) == 0 and file_count >= 3:
        warnings.append(
            "IPLAN-006: file_count >= 3 but no implementation contracts. Consider adding contracts for shared interfaces."
        )
        return

    passes.append(f"IPLAN-006: implementation_contracts validated with {len(contracts)} contracts and {file_count} files")


def run_iplan_validation_checks(
    *,
    yaml_data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Run all IPLAN-specific validation checks."""
    check_iplan_readiness_score(yaml_data, errors, warnings, passes)
    check_file_manifest(yaml_data, errors, warnings, passes)
    check_execution_commands(yaml_data, errors, warnings, passes)
    check_session_handoff(yaml_data, errors, warnings, passes)
    check_tdd_traceability(yaml_data, errors, warnings, passes)
    check_implementation_contracts(yaml_data, errors, warnings, passes)
