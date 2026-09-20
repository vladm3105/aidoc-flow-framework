#!/usr/bin/env python3
"""CHG Governance Linter — validates CHG documents against governance rules.

Canonical copy: `sdd_doc_lint/chg_lint.py` (the former `scripts/chg_lint.py`
duplicate was removed by CLEANUP-001; run via `python -m sdd_doc_lint.chg_lint`
or `python sdd_doc_lint/chg_lint.py`).

Checks:
  CHG-L001: Status lifecycle (§3.3) — status must follow Proposed → Approved → In-Progress → Implemented → Completed
  CHG-L002: Gate approval (§3.1) — C3 changes must have gate_approval.approver
  CHG-L003: CHG scope (§3.4 items 13-14) — no code implementation steps in CHG
  CHG-L004: IPLAN reference (§3.1.1) — CHG must reference an IPLAN for code changes
  CHG-L005: SDD-first order (§3.1.1) — SDD lifecycle steps must appear before IPLAN creation
  CHG-L006: SDD lifecycle completeness (§3.4.1 C16) — `implementation.steps` with
    phase `sdd_lifecycle` must exist when SDD documents are modified
  CHG-L007: SDD entry metadata (§3.4.1 C17) — every `sdd_lifecycle` step declares
    artifact + status; archive_path/new_version required except IPLAN-create steps
  CHG-L008: Archive path convention (§3.4.1 C18) — archive paths use CHG-ID
    format (`.../archive/<CHG-ID>/...`), never date-based paths
  CHG-L009: Version bump (§3.4.1 C19) — new_version must differ from current
    when stated
  CHG-L010: Supersedes completeness (§3.4.1 C20) — `change_control.supersedes`
    must list every archived document with its full archive path
  CHG-L011: Cited EARS/BDD IDs exist (§3.4.1 D21/D22) — every EARS/BDD ID cited
    in the CHG must exist in the referenced EARS/BDD document (warning-level:
    referenced files may live in the consuming project, not this repo)

Usage:
  python -m sdd_doc_lint.chg_lint <chg-file.yaml>
  python sdd_doc_lint/chg_lint.py <chg-file.yaml>
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


def _sdd_lifecycle_steps(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return implementation steps with phase `sdd_lifecycle`."""
    implementation = data.get("implementation", {})
    if not isinstance(implementation, dict):
        return []
    steps = implementation.get("steps", [])
    if not isinstance(steps, list):
        return []
    return [s for s in steps if isinstance(s, dict) and str(s.get("phase", "")).lower() == "sdd_lifecycle"]


def check_sdd_lifecycle_completeness(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L006: sdd_lifecycle steps must exist when SDD documents are modified (§3.4.1 C16)."""
    modified = data.get("implementation", {})
    artifacts: list[dict[str, Any]] = []
    if isinstance(modified, dict):
        raw = modified.get("artifacts_modified", [])
        if isinstance(raw, list):
            artifacts = [a for a in raw if isinstance(a, dict)]
    steps = _sdd_lifecycle_steps(data)
    if artifacts and not steps:
        errors.append(
            f"CHG-L006: {len(artifacts)} artifact(s) in artifacts_modified but no "
            "implementation.steps with phase 'sdd_lifecycle' — every modified SDD "
            "document needs an archive → rewrite → supersedes → version-bump step"
        )
        return
    passes.append("CHG-L006: SDD lifecycle completeness check passed")


def check_sdd_entry_metadata(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L007: every sdd_lifecycle step declares artifact + archive metadata (§3.4.1 C17)."""
    steps = _sdd_lifecycle_steps(data)
    if not steps:
        passes.append("CHG-L007: no sdd_lifecycle steps to check")
        return
    bad = 0
    for step in steps:
        title = step.get("step", step.get("title", "?"))
        if not step.get("artifact"):
            errors.append(f"CHG-L007: sdd_lifecycle step '{title}' missing 'artifact'")
            bad += 1
        if not step.get("status"):
            errors.append(f"CHG-L007: sdd_lifecycle step '{title}' missing 'status'")
            bad += 1
        # IPLAN-create steps legitimately carry no archive metadata; everything
        # else must archive → rewrite, so null archive_path/new_version is an error.
        is_iplan_create = "iplan" in str(step.get("artifact", "")).upper()
        if not is_iplan_create:
            if step.get("archive_path") in (None, "null", ""):
                errors.append(
                    f"CHG-L007: sdd_lifecycle step '{title}' has null archive_path — "
                    "non-IPLAN-create entries must archive the current version first"
                )
                bad += 1
            if step.get("new_version") in (None, "null", ""):
                errors.append(
                    f"CHG-L007: sdd_lifecycle step '{title}' has null new_version — "
                    "non-IPLAN-create entries must state the rewritten version"
                )
                bad += 1
    if bad == 0:
        passes.append(f"CHG-L007: all {len(steps)} sdd_lifecycle step(s) carry required metadata")


def check_archive_path_convention(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L008: archive paths use CHG-ID format, not date-based (§3.4.1 C18)."""
    import re

    steps = _sdd_lifecycle_steps(data)
    paths = [str(s.get("archive_path", "")) for s in steps if s.get("archive_path") not in (None, "null", "")]
    if not paths:
        passes.append("CHG-L008: no archive paths to check")
        return
    bad = 0
    date_pat = re.compile(r"(19|20)\d{2}[-_/](0[1-9]|1[0-2])[-_/](0[1-9]|[12]\d|3[01])")
    for p in paths:
        if date_pat.search(p):
            errors.append(f"CHG-L008: archive path '{p}' looks date-based — use .../archive/<CHG-ID>/... instead")
            bad += 1
        elif "archive/" not in p:
            warnings.append(f"CHG-L008: archive path '{p}' does not contain an 'archive/' segment")
    if bad == 0:
        passes.append(f"CHG-L008: all {len(paths)} archive path(s) follow CHG-ID convention")


def check_version_bump(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L009: new_version must differ from current when stated (§3.4.1 C19)."""
    steps = _sdd_lifecycle_steps(data)
    checked = 0
    for step in steps:
        title = step.get("step", step.get("title", "?"))
        new_version = step.get("new_version")
        current = step.get("current_version", step.get("version"))
        if new_version in (None, "null", ""):
            continue
        checked += 1
        if current not in (None, "null", "") and str(new_version) == str(current):
            errors.append(
                f"CHG-L009: sdd_lifecycle step '{title}' new_version '{new_version}' "
                "equals current version — a rewrite must bump the version"
            )
    if checked == 0:
        passes.append("CHG-L009: no stated new_version to compare")
    else:
        passes.append(f"CHG-L009: {checked} new_version(s) differ from current")


def check_supersedes_completeness(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L010: supersedes lists every archived document with full path (§3.4.1 C20)."""
    change_control = data.get("change_control", {})
    supersedes = change_control.get("supersedes", []) if isinstance(change_control, dict) else []
    if not isinstance(supersedes, list):
        errors.append("CHG-L010: change_control.supersedes must be a list")
        return
    archived = [
        str(s.get("archive_path", ""))
        for s in _sdd_lifecycle_steps(data)
        if s.get("archive_path") not in (None, "null", "")
    ]
    if not archived:
        passes.append("CHG-L010: no archived documents to cross-check")
        return
    supersedes_text = " ".join(str(s) for s in supersedes)
    missing = [p for p in archived if p not in supersedes_text]
    if not supersedes and archived:
        errors.append(
            f"CHG-L010: {len(archived)} archived document(s) but change_control.supersedes "
            "is empty — every archived path must be listed with its full path"
        )
    elif missing:
        for p in missing:
            errors.append(f"CHG-L010: archived path '{p}' missing from change_control.supersedes")
    else:
        passes.append(f"CHG-L010: supersedes covers all {len(archived)} archived document(s)")


def check_cited_ids_exist(
    data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
    file_path: Path,
) -> None:
    """CHG-L011: cited EARS/BDD IDs exist in the referenced documents (§3.4.1 D21/D22).

    Warning-level: in the framework-only repo the referenced EARS/BDD documents
    usually live in the consuming project, not beside the CHG, so absence is
    unverifiable rather than a proven fabrication.
    """
    import re

    text = file_path.read_text(encoding="utf-8", errors="replace") if file_path.exists() else ""
    cited_ears = set(re.findall(r"\bEARS-[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*", text))
    cited_bdd = set(re.findall(r"\bBDD-[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*", text))
    if not cited_ears and not cited_bdd:
        passes.append("CHG-L011: no EARS/BDD IDs cited")
        return
    root = file_path.parent
    checked = 0
    for doc_id in sorted(cited_ears | cited_bdd):
        # Heuristic: a same-directory or nearby file carrying the doc's base ID.
        base = doc_id.split(".")[0]
        candidates = list(root.rglob(f"{base}.*")) if root.exists() else []
        if not candidates:
            warnings.append(
                f"CHG-L011: cited '{doc_id}' but no {base}.* document found near "
                f"{file_path.name} — verify it exists in the consuming project"
            )
            continue
        checked += 1
        haystack = " ".join(p.read_text(encoding="utf-8", errors="replace") for p in candidates[:5])
        if doc_id not in haystack:
            warnings.append(f"CHG-L011: cited '{doc_id}' not found in {base}.* near {file_path.name}")
    passes.append(f"CHG-L011: cited-ID existence checked ({checked} verifiable reference(s))")


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
    check_sdd_lifecycle_completeness(data, errors, warnings, passes)
    check_sdd_entry_metadata(data, errors, warnings, passes)
    check_archive_path_convention(data, errors, warnings, passes)
    check_version_bump(data, errors, warnings, passes)
    check_supersedes_completeness(data, errors, warnings, passes)
    check_cited_ids_exist(data, errors, warnings, passes, file_path)

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
