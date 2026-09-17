#!/usr/bin/env python3
"""CHG Governance Linter — validates CHG documents against governance rules.

Checks:
  CHG-L001: Status lifecycle (§3.3) — status must follow Proposed → Approved → In-Progress → Implemented → Completed
  CHG-L002: Gate approval (§3.1) — C3 changes must have gate_approval.approver
  CHG-L003: CHG scope (§3.4 items 13-14) — no code implementation steps in CHG
  CHG-L004: IPLAN reference (§3.1.1) — CHG must reference an IPLAN for code changes
  CHG-L005: SDD-first order (§3.1.1) — SDD lifecycle steps must appear before IPLAN creation
  CHG-L006: SDD lifecycle completeness (§3.4.1 C16) — sdd_lifecycle must list every
    modified SDD document (cross-checked against artifacts_modified)
  CHG-L007: SDD lifecycle metadata (§3.4.1 C17-C19) — each entry must carry layer,
    document, action, a CHG-ID-format archive_path, and a bumped new_version
  CHG-L008: Supersedes completeness (§3.4.1 C20) — supersedes must list every
    archived document with its full archive path
  CHG-L009: EARS/BDD traceability (§3.4.1 D21-D22) — EARS/BDD IDs cited anywhere in
    the CHG must exist in the referenced EARS/BDD documents

Usage:
  python scripts/chg_lint.py <chg-file.yaml> [--sdd-root <dir>]
  python scripts/chg_lint.py docs/sdd/09-CHG/*.yaml --sdd-root docs/sdd

  The lifecycle/traceability checks (L006-L009) resolve SDD document files
  relative to --sdd-root (default: docs/sdd beside the 09-CHG directory
  containing the CHG file). When a referenced file cannot be found, the
  relevant check reports a warning (not an error) so the standalone linter
  stays usable without a full SDD tree.
"""

from __future__ import annotations

import argparse
import re
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


# Valid sdd_lifecycle layer codes. EARS/BDD are accepted alongside the archive
# convention's SPEC/TDD/IPLAN layers: recent CHGs extend all four SDD layers and
# the CHG-06 precedent archived 03_EARS/04_BDD snapshots.
VALID_LIFECYCLE_LAYERS = frozenset({"03_EARS", "04_BDD", "06_SPEC", "07_TDD", "08_IPLAN"})

# Layers whose documents carry versioned element IDs citable for D21/D22.
TRACEABLE_LAYERS = frozenset({"03_EARS", "04_BDD"})

# Element ID form shared with the structural linter's id_patterns.element
# (framework/registry/LAYER_REGISTRY.yaml). Full form TYPE.NN.NN.<hex 4-8>;
# legacy short form TYPE.NN.<suffix> is accepted for D21/D22 existence checks
# only — malformed IDs remain the structural linter's (ID03) job.
ELEMENT_ID_FULL = re.compile(r"^[A-Z]+\.\d{2,}\.\d{2,}\.[A-Za-z0-9]{4,8}$")
ELEMENT_ID_SHORT = re.compile(r"^[A-Z]+-\d{2,}$|^[A-Z]+\.\d{2,}\.[A-Za-z0-9][A-Za-z0-9_.-]*$")


def _lifecycle_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return sdd_lifecycle entries as a list (tolerates the CHG-22 grouped variant)."""
    lifecycle = data.get("sdd_lifecycle", [])
    if not isinstance(lifecycle, list):
        return []
    flat: list[dict[str, Any]] = []
    for item in lifecycle:
        if not isinstance(item, dict):
            continue
        # CHG-22 variant: {"layer": ..., "documents": [{id, action, ...}, ...]}
        docs = item.get("documents")
        if isinstance(docs, list):
            for doc in docs:
                if isinstance(doc, dict):
                    merged = dict(item)
                    merged.update(doc)
                    merged.pop("documents", None)
                    flat.append(merged)
        else:
            flat.append(item)
    return flat


def _entry_doc_name(entry: dict[str, Any]) -> str | None:
    doc = entry.get("document") or entry.get("id")
    return str(doc) if doc else None


def _modified_doc_names(data: dict[str, Any]) -> set[str]:
    """Document names the CHG claims to modify (artifacts_modified paths' stems)."""
    names: set[str] = set()
    artifacts = data.get("artifacts_modified", [])
    if isinstance(artifacts, list):
        for item in artifacts:
            if not isinstance(item, dict):
                continue
            path = item.get("path") or item.get("file") or item.get("id") or ""
            stem = Path(str(path)).stem
            if stem:
                names.add(stem)
    return names


def check_lifecycle_completeness(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L006: sdd_lifecycle must list every modified SDD document (§3.4.1 C16)."""
    entries = _lifecycle_entries(data)
    if not entries and not _modified_doc_names(data):
        passes.append("CHG-L006: no SDD lifecycle or modified artifacts declared")
        return

    listed = {_entry_doc_name(e) for e in entries}
    listed.discard(None)
    # IPLAN-create entries name a document that does not exist yet — resolve by
    # prefix so "IPLAN-42_cabinet_review_gap_remediation" matches either form.
    listed_prefixes = {name.split("_")[0] if "_" in name else name for name in listed}

    missing = sorted(
        name for name in _modified_doc_names(data)
        if name not in listed and (name.split("_")[0] if "_" in name else name) not in listed_prefixes
    )
    if missing:
        errors.append(
            "CHG-L006: artifacts_modified lists documents missing from sdd_lifecycle: "
            + ", ".join(missing)
        )
    else:
        passes.append("CHG-L006: sdd_lifecycle lists every modified SDD document")


def check_lifecycle_metadata(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L007: each entry needs layer/document/action/archive_path/new_version (§3.4.1 C17-C19)."""
    entries = _lifecycle_entries(data)
    if not entries:
        passes.append("CHG-L007: no sdd_lifecycle entries to check")
        return

    bad = 0
    chg_id = str(data.get("id") or data.get("change_control", {}).get("chg_id") or "")
    for entry in entries:
        name = _entry_doc_name(entry) or "<unnamed>"
        layer = entry.get("layer")
        action = entry.get("action")
        archive_path = entry.get("archive_path")
        new_version = entry.get("new_version")

        if layer not in VALID_LIFECYCLE_LAYERS:
            errors.append(f"CHG-L007: entry '{name}' has unknown layer '{layer}' — want one of {sorted(VALID_LIFECYCLE_LAYERS)}")
            bad += 1
        if not action:
            errors.append(f"CHG-L007: entry '{name}' is missing action (extend|rewrite|create)")
            bad += 1
        # IPLAN-create entries name a document that does not exist yet — there is
        # nothing to archive, so archive_path/new_version are not required.
        if layer == "08_IPLAN" and str(action).lower() == "create":
            continue
        if not archive_path:
            errors.append(f"CHG-L007: entry '{name}' has null archive_path — archive the pre-change version first (§3.4.1 C17)")
            bad += 1
        elif chg_id and chg_id not in str(archive_path):
            warnings.append(f"CHG-L007: entry '{name}' archive_path '{archive_path}' does not use CHG-ID format (§3.4.1 C18)")
        if new_version is None or str(new_version).strip() in ("", "null"):
            errors.append(f"CHG-L007: entry '{name}' has null new_version — record the bumped version (§3.4.1 C19)")
            bad += 1

    if bad == 0:
        passes.append("CHG-L007: sdd_lifecycle entries carry layer/action/archive_path/new_version")


def check_supersedes(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """CHG-L008: supersedes must list every archived document with full path (§3.4.1 C20)."""
    entries = _lifecycle_entries(data)
    archived = sorted(str(e.get("archive_path")) for e in entries if e.get("archive_path"))
    if not archived:
        passes.append("CHG-L008: no archived documents to supersede")
        return

    change_control = data.get("change_control", {})
    supersedes = change_control.get("supersedes", []) if isinstance(change_control, dict) else []
    if not isinstance(supersedes, list):
        errors.append("CHG-L008: change_control.supersedes must be a list of archived paths")
        return
    superseded = " ".join(str(s) for s in supersedes)

    missing = [p for p in archived if p not in superseded]
    if missing:
        errors.append(
            "CHG-L008: supersedes omits archived documents (§3.4.1 C20): " + ", ".join(missing)
        )
    else:
        passes.append("CHG-L008: supersedes lists every archived document")


def _element_ids_in_text(text: str) -> set[str]:
    """Candidate EARS/BDD element IDs cited in free text (descriptions, what/why)."""
    ids: set[str] = set()
    for m in re.finditer(r"\b(EARS|BDD)\.\d{2,}\.\d{2,}\.[A-Za-z0-9]{4,8}\b", text):
        ids.add(m.group(0))
    return ids


def _element_ids_in_doc(doc: Any) -> set[str]:
    """All element IDs declared anywhere in a parsed SDD document."""
    ids: set[str] = set()
    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "id" and isinstance(value, str) and ELEMENT_ID_SHORT.match(value):
                    ids.add(value)
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str):
            for m in re.finditer(r"\b(EARS|BDD)\.\d{2,}\.\d{2,}\.[A-Za-z0-9]{4,8}\b", node):
                ids.add(m.group(0))
    walk(doc)
    return ids


def _resolve_sdd_file(sdd_root: Path | None, layer: str, doc_name: str) -> Path | None:
    if sdd_root is None:
        return None
    stem = doc_name if doc_name.endswith((".yaml", ".yml", ".md")) else doc_name + ".yaml"
    candidate = sdd_root / layer / stem
    if candidate.exists():
        return candidate
    alt = sdd_root / layer / (doc_name + ".yml")
    if alt.exists():
        return alt
    return None


def check_traceability(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str], ctx: dict[str, Any]) -> None:
    """CHG-L009: EARS/BDD IDs cited in the CHG must exist in-tree (§3.4.1 D21-D22)."""
    texts: list[str] = []

    def collect(node: Any) -> None:
        if isinstance(node, dict):
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)
        elif isinstance(node, str):
            texts.append(node)

    for section in ("change_description", "implementation", "issues"):
        collect(data.get(section))
    # sdd_lifecycle `changes` fields also cite new IDs (e.g. "Adds EARS.01.03.8e4b").
    collect(data.get("sdd_lifecycle"))

    cited: set[str] = set()
    for text in texts:
        cited |= _element_ids_in_text(text)

    if not cited:
        passes.append("CHG-L009: no EARS/BDD element IDs cited")
        return

    sdd_root: Path | None = ctx.get("sdd_root")
    if sdd_root is None:
        warnings.append(
            "CHG-L009: cannot verify cited EARS/BDD IDs without --sdd-root ("
            + ", ".join(sorted(cited)) + ")"
        )
        return

    # Pool every element ID declared in the lifecycle's EARS/BDD documents.
    declared: set[str] = set()
    missing_files: list[str] = []
    for entry in _lifecycle_entries(data):
        layer = entry.get("layer")
        if layer not in TRACEABLE_LAYERS:
            continue
        name = _entry_doc_name(entry)
        if not name:
            continue
        path = _resolve_sdd_file(sdd_root, layer, name)
        if path is None:
            missing_files.append(f"{layer}/{name}")
            continue
        try:
            with open(path) as f:
                declared |= _element_ids_in_doc(yaml.safe_load(f))
        except yaml.YAMLError as e:
            warnings.append(f"CHG-L009: cannot parse {path}: {e}")

    if missing_files:
        warnings.append(
            "CHG-L009: lifecycle SDD files not found under --sdd-root, traceability unchecked for: "
            + ", ".join(sorted(set(missing_files)))
        )
        return

    # Exact match only. A cited full-form ID resolves iff the identical string is
    # declared in-tree; a shared TYPE.NN.NN stem is NOT sufficient (a wrong hash
    # with a right stem is exactly the fabrication D21/D22 exist to catch).
    unknown = sorted(c for c in cited if c not in declared)
    if unknown:
        errors.append(
            "CHG-L009: cited EARS/BDD IDs not found in lifecycle SDD documents (§3.4.1 D21-D22): "
            + ", ".join(unknown)
        )
    else:
        passes.append(f"CHG-L009: all {len(cited)} cited EARS/BDD IDs resolve in-tree")


def lint_chg(file_path: Path, sdd_root: Path | None = None) -> tuple[list[str], list[str], list[str]]:
    """Lint a single CHG file and return (errors, warnings, passes)."""
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    ctx: dict[str, Any] = {"sdd_root": sdd_root}

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

    # Resolve the default SDD root: docs/sdd beside the 09-CHG dir holding the file.
    if ctx["sdd_root"] is None:
        if file_path.parent.name == "09-CHG" and file_path.parent.parent.name == "sdd":
            candidate = file_path.parent.parent
            if candidate.is_dir():
                ctx["sdd_root"] = candidate

    # Run all checks
    check_status_lifecycle(data, errors, warnings, passes)
    check_gate_approval(data, errors, warnings, passes)
    check_chg_scope(data, errors, warnings, passes)
    check_iplan_reference(data, errors, warnings, passes)
    check_sdd_first_order(data, errors, warnings, passes)
    check_lifecycle_completeness(data, errors, warnings, passes)
    check_lifecycle_metadata(data, errors, warnings, passes)
    check_supersedes(data, errors, warnings, passes)
    check_traceability(data, errors, warnings, passes, ctx)

    return errors, warnings, passes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CHG governance linter (§3.4.1).")
    parser.add_argument("files", nargs="+", help="CHG file(s) to lint")
    parser.add_argument(
        "--sdd-root",
        default=None,
        help="SDD tree root holding 03_EARS/04_BDD/... (default: docs/sdd beside the CHG file)",
    )
    args = parser.parse_args(argv)

    sdd_root = Path(args.sdd_root) if args.sdd_root else None
    if sdd_root is not None and not sdd_root.is_dir():
        print(f"❌ --sdd-root not a directory: {sdd_root}", file=sys.stderr)
        return 2

    total_errors = 0
    total_warnings = 0

    for arg in args.files:
        path = Path(arg)
        if not path.exists():
            print(f"❌ File not found: {path}", file=sys.stderr)
            total_errors += 1
            continue

        errors, warnings, passes = lint_chg(path, sdd_root)
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
