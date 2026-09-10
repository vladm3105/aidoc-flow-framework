#!/usr/bin/env python3
"""CHG Governance Linter — validates CHG documents against governance rules.

Checks:
  CHG-L001: Status lifecycle (§3.3) — status must follow Proposed → Approved → In-Progress → Implemented → Completed
  CHG-L002: Gate approval (§3.1) — C3 changes must have gate_approval.approver
  CHG-L003: CHG scope (§3.4 items 13-14) — no code implementation steps in CHG
  CHG-L004: IPLAN reference (§3.1.1) — CHG must reference an IPLAN for code changes
  CHG-L005: SDD-first order (§3.1.1) — SDD lifecycle steps must appear before IPLAN creation

Usage:
  python scripts/chg_lint.py <chg-file.yaml>
  python scripts/chg_lint.py docs/sdd/09-CHG/*.yaml
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(3)


# Valid status transitions (must follow this order)
VALID_STATUS_ORDER = ["Proposed", "Approved", "In-Progress", "Implemented", "Completed"]


def check_status_lifecycle(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L001: Status must follow lifecycle (§3.3)."""
    change_control = data.get("change_control", {})
    if not isinstance(change_control, dict):
        errors.append("CHG-L001: change_control section missing")
        return

    status = change_control.get("status")
    if not status:
        errors.append("CHG-L001: change_control.status missing")
        return

    if status not in VALID_STATUS_ORDER:
        errors.append(f"CHG-L001: invalid status '{status}'. Must be one of {VALID_STATUS_ORDER}")
        return

    # Check for skipped stages
    date_approved = change_control.get("date_approved")
    date_implemented = change_control.get("date_implemented")

    if status in ("In-Progress", "Implemented", "Completed") and not date_approved:
        errors.append(f"CHG-L001: status is '{status}' but date_approved is null — cannot skip 'Approved' stage")

    if status in ("Implemented", "Completed") and not date_implemented:
        warnings.append(f"CHG-L001: status is '{status}' but date_implemented is null")

    # Check gate approval for C3
    level = change_control.get("change_level")
    gate_approval = data.get("gate_approval", {})

    if level == "C3" and status != "Proposed":
        if isinstance(gate_approval, dict):
            approver = gate_approval.get("approver")
            if not approver or approver == "null":
                errors.append(f"CHG-L001: C3 change with status '{status}' but gate_approval.approver is null")
        else:
            errors.append(f"CHG-L001: C3 change with status '{status}' but no gate_approval section")

    passes.append(f"CHG-L001: status lifecycle check passed (status={status})")


def check_gate_approval(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L002: C3 changes must have gate approval (§3.1)."""
    change_control = data.get("change_control", {})
    gate_approval = data.get("gate_approval", {})

    level = change_control.get("change_level")
    if level != "C3":
        passes.append(f"CHG-L002: gate approval check skipped (level={level})")
        return

    if not isinstance(gate_approval, dict):
        errors.append("CHG-L002: C3 change requires gate_approval section")
        return

    approver = gate_approval.get("approver")
    gate = gate_approval.get("gate")
    approval_date = gate_approval.get("approval_date")

    if not approver or approver == "null":
        errors.append("CHG-L002: C3 change requires gate_approval.approver")
    if not gate:
        errors.append("CHG-L002: C3 change requires gate_approval.gate")
    if not approval_date:
        warnings.append("CHG-L002: gate_approval.approval_date is null")

    if approver and approver != "null" and gate:
        passes.append(f"CHG-L002: gate approval present (approver={approver}, gate={gate})")


def check_chg_scope(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L003: No code implementation steps in CHG (§3.4 items 13-14)."""
    implementation = data.get("implementation", {})
    if not isinstance(implementation, dict):
        passes.append("CHG-L003: no implementation section found")
        return

    steps = implementation.get("steps", [])
    if not isinstance(steps, list):
        passes.append("CHG-L003: no implementation steps found")
        return

    code_keywords = ["implement", "code", "function", "struct", "interface", "method", "handler"]
    code_step_count = 0

    for step in steps:
        if not isinstance(step, dict):
            continue
        title = str(step.get("title", "")).lower()
        description = str(step.get("description", "")).lower()
        phase = str(step.get("phase", "")).lower()

        # Check if this looks like a code implementation step
        if phase in ("code", "implementation", "code_implementation"):
            code_step_count += 1
            errors.append(f"CHG-L003: step '{step.get('title')}' has phase '{phase}' — code steps belong in IPLAN")
        elif any(kw in title for kw in code_keywords) and "sdd" not in phase and "iplan" not in phase:
            # Heuristic: title contains code keywords but isn't SDD or IPLAN phase
            code_step_count += 1
            warnings.append(f"CHG-L003: step '{step.get('title')}' may be a code step (check if it belongs in IPLAN)")

    if code_step_count == 0:
        passes.append("CHG-L003: no code implementation steps found in CHG")


def check_iplan_reference(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L004: CHG must reference an IPLAN for code changes (§3.1.1)."""
    artifacts = data.get("sdd_lifecycle", {})
    if not isinstance(artifacts, dict):
        # Try artifacts_modified
        artifacts = data.get("implementation", {})
        if not isinstance(artifacts, dict):
            passes.append("CHG-L004: no artifacts section found")
            return

    # Look for IPLAN references
    has_iplan = False

    # Check sdd_lifecycle
    lifecycle = data.get("sdd_lifecycle", [])
    if isinstance(lifecycle, list):
        for item in lifecycle:
            if isinstance(item, dict) and item.get("layer") == "08_IPLAN":
                has_iplan = True
                break

    # Check artifacts_modified
    artifacts_modified = artifacts.get("artifacts_modified", [])
    if isinstance(artifacts_modified, list):
        for item in artifacts_modified:
            if isinstance(item, dict) and "IPLAN" in str(item.get("id", "")):
                has_iplan = True
                break

    if not has_iplan:
        warnings.append("CHG-L004: no IPLAN reference found — CHG should reference an IPLAN for code changes")
    else:
        passes.append("CHG-L004: IPLAN reference found")


def check_sdd_first_order(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L005: SDD lifecycle steps must appear before IPLAN creation (§3.1.1)."""
    implementation = data.get("implementation", {})
    if not isinstance(implementation, dict):
        passes.append("CHG-L005: no implementation section found")
        return

    steps = implementation.get("steps", [])
    if not isinstance(steps, list):
        passes.append("CHG-L005: no implementation steps found")
        return

    sdd_phases = {"sdd_lifecycle", "sdd", "archive", "rewrite"}
    iplan_phases = {"iplan_creation", "iplan"}
    code_phases = {"code", "implementation", "code_implementation"}

    last_sdd_index = -1
    first_iplan_index = len(steps)
    first_code_index = len(steps)

    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        phase = str(step.get("phase", "")).lower()
        title = str(step.get("title", "")).lower()

        if any(sp in phase for sp in sdd_phases) or "archive" in title or "rewrite" in title:
            last_sdd_index = max(last_sdd_index, i)
        elif any(ip in phase for ip in iplan_phases) or "iplan" in title:
            first_iplan_index = min(first_iplan_index, i)
        elif any(cp in phase for cp in code_phases) or "implement" in title:
            first_code_index = min(first_code_index, i)

    if last_sdd_index >= 0 and first_iplan_index < len(steps):
        if first_iplan_index < last_sdd_index:
            errors.append("CHG-L005: IPLAN creation appears before SDD lifecycle steps — SDD must come first")
        else:
            passes.append("CHG-L005: SDD lifecycle steps appear before IPLAN creation")

    if first_code_index < len(steps):
        if first_code_index < first_iplan_index:
            errors.append("CHG-L005: code implementation appears before IPLAN creation — IPLAN must come first")
        elif last_sdd_index >= 0 and first_code_index < last_sdd_index:
            errors.append("CHG-L005: code implementation appears before SDD lifecycle steps")
        else:
            passes.append("CHG-L005: code implementation order correct")


def lint_chg(file_path: Path) -> tuple[list[str], list[str], list[str]]:
    """Lint a single CHG file and return (errors, warnings, passes)."""
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []

    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {e}")
        return errors, warnings, passes
    except FileNotFoundError:
        errors.append(f"File not found: {file_path}")
        return errors, warnings, passes

    if not isinstance(data, dict):
        errors.append("CHG document is not a valid YAML mapping")
        return errors, warnings, passes

    # Run all checks
    check_status_lifecycle(data, errors, warnings, passes)
    check_gate_approval(data, errors, warnings, passes)
    check_chg_scope(data, errors, warnings, passes)
    check_iplan_reference(data, errors, warnings, passes)
    check_sdd_first_order(data, errors, warnings, passes)

    return errors, warnings, passes


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print("Usage: chg_lint.py <chg-file.yaml> [chg-file2.yaml ...]", file=sys.stderr)
        return 2

    total_errors = 0
    total_warnings = 0

    for arg in argv:
        path = Path(arg)
        if not path.exists():
            print(f"❌ File not found: {path}", file=sys.stderr)
            total_errors += 1
            continue

        errors, warnings, passes = lint_chg(path)
        total_errors += len(errors)
        total_warnings += len(warnings)

        print(f"\n{'='*60}")
        print(f"CHG Lint: {path.name}")
        print(f"{'='*60}")

        if errors:
            print("\n❌ ERRORS:")
            for e in errors:
                print(f"  - {e}")

        if warnings:
            print("\n⚠️  WARNINGS:")
            for w in warnings:
                print(f"  - {w}")

        if passes:
            print("\n✅ PASSES:")
            for p in passes:
                print(f"  - {p}")

        if not errors and not warnings:
            print("\n✅ All checks passed")

    print(f"\n{'='*60}")
    print(f"Summary: {total_errors} error(s), {total_warnings} warning(s)")
    print(f"{'='*60}")

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
