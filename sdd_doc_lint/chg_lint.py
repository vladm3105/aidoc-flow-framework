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
    in the CHG must exist in the referenced EARS/BDD document. Exact match
    (error) when the tree is verifiable via --sdd-root; nearby-heuristic
    (warning) otherwise — ported from #653, adapted to the canonical
    implementation.steps schema (see GOV-014..GOV-017 in LINT_RULES.md)
  CHG-L012: SDD sync on IPLAN completion (DOC_GOVERNANCE_CORE.md §IPLAN
    Lifecycle) — when a CHG moves a Completed IPLAN's SPEC/TDD check into the
    same change, the IPLAN's `completion_spec_sync:` field must show the check
    was done (warning-level: the CHG author attests by filling the field; the
    linter validates the attestation shape, not the codebase)
  CHG-L013: Flow misclassification guard (§3.1.3 router, GOV-018) — a code/script
    manifest with an empty SDD lifecycle but no `direct` source, no IPLAN
    reference, or no `parent_iplan` where F4 applies, is an error naming the
    suspected flow (F2/F3/F4)
  CHG-L014: F3 seed/module lifecycle coverage (§3.1.3 router, GOV-020) —
    a CHG from a lifecycle-carrying source (upstream/midstream/design, spec,
    reconciliation) touching seed/module docs must cover them: seed touches
    need `seed_scope` (decision no-change | create | supersede; supersede
    requires non-empty `entries`), module touches need a `module_lifecycle`
    entry. Other sources pass through untouched.
  CHG-L015: Lifecycle-entry attribution (flows doc §4, GOV-021) — every
    `seed_scope.entries[]` / `module_lifecycle` entry on a lifecycle-carrying
    CHG must carry a non-empty `author` (agent id + supervising human);
    module entries must also carry `chg_ref`. Deterministic half of GOV-021;
    carrier completeness stays with the reviewer lens.

Usage:
  python -m sdd_doc_lint.chg_lint [--sdd-root <dir>] <chg-file.yaml>
  python sdd_doc_lint/chg_lint.py [--sdd-root <dir>] <chg-file.yaml>

  --sdd-root points at the SDD tree root holding 03_EARS/04_BDD/... and
  switches CHG-L011 to exact-match (error) verification; without it L011
  falls back to the nearby-heuristic (warning).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

try:
    from sdd_doc_lint._common import load_yaml_file, yaml
except ImportError:
    from _common import load_yaml_file, yaml


# Valid status transitions (must follow this order)
VALID_STATUS_ORDER = ["Proposed", "Approved", "In-Progress", "Implemented", "Completed"]

# Rule IDs this linter can emit. Imported by the catalog guard
# (tests/conformance/test_lint_catalog.py) so the linter cannot drift out of
# sync with framework/governance/LINT_RULES.md (#715).
CODES = frozenset(f"CHG-L{i:03d}" for i in range(1, 16))


def check_status_lifecycle(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
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
        errors.append(
            f"CHG-L001: status is '{status}' but date_approved is null — cannot skip 'Approved' stage"
        )

    if status in ("Implemented", "Completed") and not date_implemented:
        warnings.append(f"CHG-L001: status is '{status}' but date_implemented is null")

    # NOTE: the C3 gate-approval check lives solely in CHG-L002 (GOV-012).
    # A copy here would double-report one defect under two codes (#668).

    passes.append(f"CHG-L001: status lifecycle check passed (status={status})")


def check_gate_approval(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """CHG-L002: C3 changes must have gate approval (§3.1)."""
    change_control = data.get("change_control", {})
    # Silent coerce, not a second report: CHG-L001 already owns the malformed
    # section (#668 single-owner rule — a copy here would double-report one
    # defect under two codes). Same idiom as the CHG-L014/L015 sites. Without
    # this a scalar change_control crashes the whole run (#712).
    if not isinstance(change_control, dict):
        change_control = {}
    gate_approval = data.get("gate_approval", {})

    level = change_control.get("change_level")
    if level != "C3":
        passes.append(f"CHG-L002: gate approval check skipped (level={level})")
        return

    # GOV-012 permits null approver while status is Proposed — approval is
    # recorded before status advances beyond Proposed, not before.
    if change_control.get("status") == "Proposed":
        passes.append("CHG-L002: Proposed C3 draft — gate approval not yet required (GOV-012)")
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


def check_chg_scope(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """CHG-L003: No code implementation steps in CHG (§3.4 items 13-14)."""
    implementation = data.get("implementation", {})
    if not isinstance(implementation, dict):
        passes.append("CHG-L003: no implementation section found")
        return

    steps = implementation.get("steps", [])
    if not isinstance(steps, list):
        passes.append("CHG-L003: no implementation steps found")
        return

    code_step_count = 0

    for step in steps:
        if not isinstance(step, dict):
            continue
        phase = str(step.get("phase", "")).lower()

        # Every step must declare its phase (§3.4 item 13).
        if not phase:
            code_step_count += 1
            errors.append(
                f"CHG-L003: step '{step.get('title')}' has no phase — every step MUST declare sdd_lifecycle or iplan_creation"
            )
        # Check if this looks like a code implementation step
        elif phase in ("code", "implementation", "code_implementation"):
            code_step_count += 1
            errors.append(
                f"CHG-L003: step '{step.get('title')}' has phase '{phase}' — code steps belong in IPLAN"
            )

    if code_step_count == 0:
        passes.append("CHG-L003: no code implementation steps found in CHG")


def check_iplan_reference(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """CHG-L004: CHG must reference an IPLAN for code changes (§3.1.1, GOV-019)."""
    # Look for IPLAN references in every location that can carry one —
    # each is optional, so all three are scanned unconditionally.
    has_iplan = False

    # Check top-level sdd_lifecycle list
    lifecycle = data.get("sdd_lifecycle", [])
    if isinstance(lifecycle, list):
        for item in lifecycle:
            if isinstance(item, dict) and item.get("layer") == "08_IPLAN":
                has_iplan = True
                break

    # Check implementation.steps[] for the canon iplan_creation phase
    # (CHG-TEMPLATE links IPLAN via steps, not via the top-level list)
    # and implementation.artifacts_modified for IPLAN ids.
    implementation = data.get("implementation", {})
    if not isinstance(implementation, dict) and not isinstance(lifecycle, list):
        passes.append("CHG-L004: no artifacts section found")
        return
    steps: list[dict[str, Any]] = []
    artifacts_modified: list[dict[str, Any]] = []
    if isinstance(implementation, dict):
        raw_steps = implementation.get("steps", [])
        if isinstance(raw_steps, list):
            steps = [s for s in raw_steps if isinstance(s, dict)]
        raw_modified = implementation.get("artifacts_modified", [])
        if isinstance(raw_modified, list):
            artifacts_modified = [a for a in raw_modified if isinstance(a, dict)]

    if not has_iplan:
        for step in steps:
            if "iplan" in str(step.get("phase", "")).lower():
                has_iplan = True
                break

    if not has_iplan:
        for item in artifacts_modified:
            if "IPLAN" in str(item.get("id", "")):
                has_iplan = True
                break

    if not has_iplan:
        errors.append(
            "CHG-L004: no IPLAN reference found — code-touching scope needs an IPLAN (GOV-019); F2 files a scoped IPLAN, F4 a bugfix-subtype IPLAN"
        )
    else:
        passes.append("CHG-L004: IPLAN reference found")


def check_sdd_first_order(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
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

    last_sdd_index = -1
    first_iplan_index = len(steps)

    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        phase = str(step.get("phase", "")).lower()
        title = str(step.get("title", "")).lower()

        if any(sp in phase for sp in sdd_phases) or "archive" in title or "rewrite" in title:
            last_sdd_index = max(last_sdd_index, i)
        elif any(ip in phase for ip in iplan_phases) or "iplan" in title:
            first_iplan_index = min(first_iplan_index, i)
        # NOTE: code phases are not ordered here — a code step in a CHG is a
        # CHG-L003 error, not an ordering input (#668).

    if last_sdd_index >= 0 and first_iplan_index < len(steps):
        if first_iplan_index < last_sdd_index:
            errors.append(
                "CHG-L005: IPLAN creation appears before SDD lifecycle steps — SDD must come first"
            )
        else:
            passes.append("CHG-L005: SDD lifecycle steps appear before IPLAN creation")


def _sdd_lifecycle_steps(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return implementation steps with phase `sdd_lifecycle`."""
    implementation = data.get("implementation", {})
    if not isinstance(implementation, dict):
        return []
    steps = implementation.get("steps", [])
    if not isinstance(steps, list):
        return []
    return [
        s
        for s in steps
        if isinstance(s, dict) and str(s.get("phase", "")).lower() == "sdd_lifecycle"
    ]


def check_sdd_lifecycle_completeness(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
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


def check_sdd_entry_metadata(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
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


def check_archive_path_convention(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """CHG-L008: archive paths use CHG-ID format, not date-based (§3.4.1 C18)."""
    steps = _sdd_lifecycle_steps(data)
    paths = [
        str(s.get("archive_path", ""))
        for s in steps
        if s.get("archive_path") not in (None, "null", "")
    ]
    if not paths:
        passes.append("CHG-L008: no archive paths to check")
        return
    bad = 0
    date_pat = re.compile(r"(19|20)\d{2}[-_/](0[1-9]|1[0-2])[-_/](0[1-9]|[12]\d|3[01])")
    for p in paths:
        if date_pat.search(p):
            errors.append(
                f"CHG-L008: archive path '{p}' looks date-based — use .../archive/<CHG-ID>/... instead"
            )
            bad += 1
        elif "archive/" not in p:
            warnings.append(f"CHG-L008: archive path '{p}' does not contain an 'archive/' segment")
    if bad == 0:
        passes.append(f"CHG-L008: all {len(paths)} archive path(s) follow CHG-ID convention")


def check_version_bump(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
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


def check_supersedes_completeness(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
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


# Layers whose documents carry versioned element IDs citable for D21/D22.
TRACEABLE_LAYERS = frozenset({"03_EARS", "04_BDD"})

# Element ID form shared with the structural linter's id_patterns.element
# (framework/registry/LAYER_REGISTRY.yaml). Full form TYPE.NN.NN.<hash 4-8>;
# legacy short form TYPE-NN.<suffix> is accepted for D21/D22 existence checks
# only — malformed IDs remain the structural linter's (ID03) job.
ELEMENT_ID_FULL = re.compile(r"^[A-Z]+\.\d{2,}\.\d{2,}\.[A-Za-z0-9]{4,8}$")
ELEMENT_ID_SHORT = re.compile(r"^[A-Z]+-\d{2,}$|^[A-Z]+\.\d{2,}\.[A-Za-z0-9][A-Za-z0-9_.-]*$")


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


def _traceable_docs_from_steps(data: dict[str, Any]) -> tuple[list[tuple[str, str]], set[str]]:
    """Derive (layer, doc) pairs from canonical `implementation.steps`.

    The canonical schema carries free-text `artifact` fields rather than
    structured layer/document entries, so layer codes (03_EARS/04_BDD) and
    EARS-/BDD- document stems are recovered by scanning step text. Steps that
    name a traceable layer but no document stem pool the whole layer
    directory. Returns (doc_pairs, whole_layers).
    """
    pairs: list[tuple[str, str]] = []
    whole: set[str] = set()
    for step in _sdd_lifecycle_steps(data):
        blob = " ".join(str(step.get(k, "")) for k in ("artifact", "step", "archive_path", "file"))
        layers = {layer for layer in TRACEABLE_LAYERS if layer in blob}
        docs = sorted(set(re.findall(r"\b((?:EARS|BDD)-\d+[A-Za-z0-9_]*)", blob)))
        for layer in sorted(layers):
            if docs:
                pairs.extend((layer, doc) for doc in docs)
            else:
                whole.add(layer)
    return pairs, whole


def check_cited_ids_exist(
    data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
    file_path: Path,
    sdd_root: Path | None = None,
) -> None:
    """CHG-L011: cited EARS/BDD IDs exist in the referenced documents (§3.4.1 D21/D22).

    Exact match (error) when the tree is verifiable via --sdd-root; the
    nearby-heuristic (warning) otherwise: in the framework-only repo the
    referenced EARS/BDD documents usually live in the consuming project, not
    beside the CHG, so absence without a tree is unverifiable rather than a
    proven fabrication. Ported from #653, adapted to the canonical
    implementation.steps schema (see GOV-014..GOV-017 in LINT_RULES.md).
    """
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

    for section in (
        "change_description",
        "implementation",
        "issues",
        "impact_assessment",
        "verification",
        "sdd_lifecycle",
    ):
        collect(data.get(section))

    cited: set[str] = set()
    for text in texts:
        cited |= _element_ids_in_text(text)

    if not cited:
        passes.append("CHG-L011: no EARS/BDD IDs cited")
        return

    if sdd_root is None:
        # Nearby-heuristic fallback (warning-level): no tree to verify against.
        root = file_path.parent
        checked = 0
        for doc_id in sorted(cited):
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
            haystack = " ".join(
                p.read_text(encoding="utf-8", errors="replace") for p in candidates[:5]
            )
            if doc_id not in haystack:
                warnings.append(
                    f"CHG-L011: cited '{doc_id}' not found in {base}.* near {file_path.name}"
                )
        passes.append(f"CHG-L011: cited-ID existence checked ({checked} verifiable reference(s))")
        return

    # Exact-match path: pool every element ID declared in the lifecycle's
    # EARS/BDD documents under --sdd-root.
    declared: set[str] = set()
    missing_files: list[str] = []
    pairs, whole_layers = _traceable_docs_from_steps(data)
    for layer, name in pairs:
        path = _resolve_sdd_file(sdd_root, layer, name)
        if path is None:
            missing_files.append(f"{layer}/{name}")
            continue
        try:
            with open(path) as f:
                declared |= _element_ids_in_doc(yaml.safe_load(f))
        except yaml.YAMLError as e:
            warnings.append(f"CHG-L011: cannot parse {path}: {e}")
    for layer in sorted(whole_layers):
        layer_dir = sdd_root / layer
        if not layer_dir.is_dir():
            missing_files.append(f"{layer}/")
            continue
        for path in sorted(layer_dir.glob("*.yaml")) + sorted(layer_dir.glob("*.yml")):
            try:
                with open(path) as f:
                    declared |= _element_ids_in_doc(yaml.safe_load(f))
            except yaml.YAMLError as e:
                warnings.append(f"CHG-L011: cannot parse {path}: {e}")

    if missing_files:
        warnings.append(
            "CHG-L011: lifecycle SDD files not found under --sdd-root, traceability unchecked for: "
            + ", ".join(sorted(set(missing_files)))
        )
        return

    # Exact match only. A cited full-form ID resolves iff the identical string
    # is declared in-tree; a shared TYPE.NN.NN stem is NOT sufficient (a wrong
    # hash with a right stem is exactly the fabrication D21/D22 exist to catch).
    unknown = sorted(c for c in cited if c not in declared)
    if unknown:
        errors.append(
            "CHG-L011: cited EARS/BDD IDs not found in lifecycle SDD documents (§3.4.1 D21-D22): "
            + ", ".join(unknown)
        )
    else:
        passes.append(f"CHG-L011: all {len(cited)} cited EARS/BDD IDs resolve in-tree")


def check_completion_spec_sync(
    data: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
    file_path: Path,
) -> None:
    """CHG-L012: SDD sync on IPLAN completion (DOC_GOVERNANCE_CORE.md §IPLAN Lifecycle).

    Warning-level (Decision C): when the CHG authorizes IPLAN work whose
    `completion_spec_sync:` block exists on a referenced IPLAN that has reached
    `Completed`, the block must attest the SPEC/TDD check (spec_checked and
    tdd_checked true, or diverged true with a named chg_ref). The linter
    validates the attestation shape on the referenced IPLAN file — it cannot
    verify the codebase comparison itself. CHGs whose referenced IPLANs carry
    no such block, or none in `Completed` status, pass silently.
    """
    text = file_path.read_text(encoding="utf-8", errors="replace") if file_path.exists() else ""
    # Resolve referenced IPLAN files: `file:` values ending in .yaml naming IPLAN-*.yaml.
    # Paths in a CHG are usually repo-root-relative; fall back to CHG-parent-relative.
    candidates: list[Path] = []
    for m in re.finditer(r"file:\s*[\"']?([^\s\"',]*?IPLAN-[^\s\"',]*\.ya?ml)[\"']?", text):
        raw = m.group(1)
        hit: Path | None = None
        for base in (Path.cwd(), file_path.parent):
            p = (base / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
            if p.exists():
                hit = p
                break
        if hit is not None and hit not in candidates:
            candidates.append(hit)
    if not candidates:
        passes.append("CHG-L012: no referenced IPLAN file to check")
        return
    checked = 0
    for iplan_path in candidates:
        try:
            iplan = yaml.safe_load(iplan_path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(iplan, dict):
            continue
        doc_control = iplan.get("document_control", {})
        if not isinstance(doc_control, dict):
            continue
        if str(doc_control.get("status", "")) != "Completed":
            continue
        sync = doc_control.get("completion_spec_sync")
        if not isinstance(sync, dict):
            continue
        checked += 1
        name = iplan_path.name
        spec_ok = sync.get("spec_checked") is True
        tdd_ok = sync.get("tdd_checked") is True
        diverged = sync.get("diverged") is True
        chg_ref = sync.get("chg_ref")
        if not spec_ok or not tdd_ok:
            warnings.append(
                f"CHG-L012: {name} is Completed but completion_spec_sync "
                "does not attest the SPEC/TDD check (spec_checked/tdd_checked must be true)"
            )
        elif diverged and chg_ref in (None, "null", ""):
            warnings.append(
                f"CHG-L012: {name} records diverged=true but names no chg_ref — "
                "name the follow-up CHG rewriting the SPEC/TDD"
            )
    if checked == 0:
        passes.append("CHG-L012: no Completed IPLAN with a completion_spec_sync block referenced")
    else:
        passes.append(
            f"CHG-L012: completion_spec_sync attestation checked on {checked} Completed IPLAN(s)"
        )


def lint_chg(
    file_path: Path, sdd_root: Path | None = None
) -> tuple[list[str], list[str], list[str]]:
    """Lint a single CHG file and return (errors, warnings, passes)."""
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []

    data, load_error = load_yaml_file(file_path)
    if load_error is not None:
        errors.append(load_error)
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
    check_cited_ids_exist(data, errors, warnings, passes, file_path, sdd_root)
    check_completion_spec_sync(data, errors, warnings, passes, file_path)
    check_flow_misclassification(data, errors, warnings, passes)
    check_seed_module_lifecycle(data, errors, warnings, passes)
    check_lifecycle_attribution(data, errors, warnings, passes)

    return errors, warnings, passes


def _is_code_path(file: object) -> bool:
    """True when an artifacts_modified file entry is executable code (not an SDD doc)."""
    if not isinstance(file, str) or not file:
        return False
    return file.endswith((".py", ".sh")) or file.startswith("hooks/") or ".github/workflows" in file


def check_flow_misclassification(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """CHG-L013: Flow misclassification guard (§3.1.3 router, GOV-018).

    Syntactic only (see CHG_REQUEST_FLOWS.md F2.4): a code/script manifest with
    an empty SDD lifecycle errors unless the shape matches F2 (source `direct`
    + IPLAN reference) or an SDD cascade / bugfix vehicle is present. A
    well-formed wrong-flow filing still lints green — semantic review owns that.
    """
    control = data.get("change_control", {})
    if not isinstance(control, dict):
        control = {}
    source = control.get("change_source")
    if source in (None, "null", ""):
        meta = data.get("metadata", {})
        if isinstance(meta, dict):
            fallback = meta.get("change_source")
            if isinstance(fallback, dict):
                fallback = fallback.get("value", source)
            if fallback not in (None, "null", ""):
                source = fallback

    impl = data.get("implementation", {})
    steps: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    if isinstance(impl, dict):
        raw_steps = impl.get("steps", [])
        if isinstance(raw_steps, list):
            steps = [s for s in raw_steps if isinstance(s, dict)]
        raw_artifacts = impl.get("artifacts_modified", [])
        if isinstance(raw_artifacts, list):
            artifacts = [a for a in raw_artifacts if isinstance(a, dict)]

    code_files = [a.get("file", "") for a in artifacts if _is_code_path(a.get("file", ""))]
    # Case-normalized like every sibling rule (#714): an uppercase phase is
    # the same phase, and must not read as an empty lifecycle here while a
    # sibling check reports it complete.
    has_sdd_steps = any(str(s.get("phase", "")).lower() == "sdd_lifecycle" for s in steps)
    has_iplan_ref = any(str(s.get("phase", "")).lower() == "iplan_creation" for s in steps) or any(
        "IPLAN" in str(a.get("id", "")) for a in artifacts
    )

    if not code_files:
        passes.append("CHG-L013: no code/script manifest — flow guard not applicable")
        return
    if has_sdd_steps:
        passes.append("CHG-L013: SDD cascade present — not a direct/bugfix-only shape")
        return
    if source == "direct" and has_iplan_ref:
        passes.append("CHG-L013: C1-direct shape (source direct + IPLAN ref, empty lifecycle)")
        return
    if source == "feedback" and not has_iplan_ref:
        errors.append(
            "CHG-L013: code/script manifest with source feedback but no IPLAN reference — "
            "post-completion repairs require a bugfix-subtype IPLAN (parent_iplan + source_chg, F4); "
            "pre-completion fixes belong on the active IPLAN itself"
        )
        return
    errors.append(
        "CHG-L013: code/script manifest with empty SDD lifecycle but change_source is not "
        f"'direct' and no IPLAN reference (source={source}) — suspected misclassified flow: "
        "F2 needs source direct + scoped IPLAN, F3 needs the SDD cascade, "
        "F4 needs a bugfix-subtype IPLAN with parent_iplan"
    )


def check_seed_module_lifecycle(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """CHG-L014: F3 seed/module lifecycle coverage (§3.1.3 router, GOV-020).

    Syntactic guard (same philosophy as CHG-L013): a CHG from a
    lifecycle-carrying source (upstream/midstream/design, plus spec for
    framework self-changes and reconciliation for Type-R) that touches seed
    or module docs must cover them — seed touches need a `seed_scope` record
    (decision no-change | create | supersede, with supersede requiring
    non-empty `entries`), module touches need a `module_lifecycle` entry.
    Coverage is presence-checked, not content-judged: a well-formed but
    wrong-scope filing still lints green — semantic review owns that. Other
    sources pass through untouched.
    """
    control = data.get("change_control", {})
    if not isinstance(control, dict):
        control = {}
    source = control.get("change_source")
    if source in (None, "null", ""):
        meta = data.get("metadata", {})
        if isinstance(meta, dict):
            fallback = meta.get("change_source")
            if isinstance(fallback, dict):
                fallback = fallback.get("value", source)
            if fallback not in (None, "null", ""):
                source = fallback

    # Lifecycle-carrying sources: the F3 family (upstream/midstream/design)
    # plus spec (framework self-changes, e.g. CHG-11's seed tier) and
    # reconciliation (Type-R) — both can touch seed/module docs (#722).
    if source not in ("upstream", "midstream", "design", "spec", "reconciliation"):
        passes.append("CHG-L014: non-lifecycle source — seed/module guard not applicable")
        return

    impl = data.get("implementation", {})
    artifacts: list[dict[str, Any]] = []
    if isinstance(impl, dict):
        raw_artifacts = impl.get("artifacts_modified", [])
        if isinstance(raw_artifacts, list):
            artifacts = [a for a in raw_artifacts if isinstance(a, dict)]

    seed_touches = [
        a.get("file", "")
        for a in artifacts
        if isinstance(a.get("file", ""), str)
        and a.get("file", "").startswith(("docs/seed/", "seed/"))
    ]
    module_touches = [
        a.get("file", "")
        for a in artifacts
        if isinstance(a.get("file", ""), str)
        and a.get("file", "").startswith(("docs/modules/", "modules/"))
    ]
    if not seed_touches and not module_touches:
        passes.append("CHG-L014: no seed/module touches — guard not applicable")
        return

    seed_scope = data.get("seed_scope", {})
    decision = seed_scope.get("decision") if isinstance(seed_scope, dict) else None
    seed_covered = decision in (
        "no-change",
        "create",
        "supersede",
    )
    if decision == "supersede":
        entries = seed_scope.get("entries", []) if isinstance(seed_scope, dict) else []
        if not isinstance(entries, list) or len(entries) == 0:
            seed_covered = False
    module_lifecycle = data.get("module_lifecycle")
    if isinstance(module_lifecycle, dict):
        entries = module_lifecycle.get("entries", module_lifecycle)
        module_covered = isinstance(entries, list) and len(entries) > 0
    else:
        module_covered = isinstance(module_lifecycle, list) and len(module_lifecycle) > 0

    problems: list[str] = []
    if seed_touches and not seed_covered:
        if decision == "supersede":
            problems.append(
                "seed docs touched with a supersede decision but empty/missing "
                "`seed_scope.entries` "
                f"({len(seed_touches)} file(s)): record one entry per superseded "
                "seed file (Phase 0a)"
            )
        else:
            problems.append(
                "seed docs touched without a seed_scope record "
                f"({len(seed_touches)} file(s)): record Phase 0a seed_scope "
                "(decision no-change with checked files cited, create, or "
                "supersede with entries)"
            )
    if module_touches and not module_covered:
        problems.append(
            "module docs touched without a module_lifecycle entry "
            f"({len(module_touches)} file(s)): record Phase 0b module_lifecycle "
            "(archive → sync → version, affected modules only)"
        )
    if problems:
        errors.append(
            "CHG-L014: F3 change touches seed/module docs without lifecycle coverage "
            "(GOV-020) — suspected F3 Phase 0a/0b omission: " + "; ".join(problems)
        )
        return
    passes.append("CHG-L014: seed/module touches covered by seed_scope/module_lifecycle")


def _lifecycle_entries(data: dict[str, Any]) -> tuple[list[Any], list[Any]]:
    """Collect (seed_entries, module_entries) from a CHG, tolerating both the
    mapping shape (`module_lifecycle: {entries: [...]}`) and the bare-list shape."""
    seed_entries: list[Any] = []
    scope = data.get("seed_scope", {})
    if isinstance(scope, dict):
        raw = scope.get("entries", [])
        if isinstance(raw, list):
            seed_entries = raw
    module_entries: list[Any] = []
    lifecycle = data.get("module_lifecycle")
    if isinstance(lifecycle, dict):
        raw = lifecycle.get("entries", lifecycle)
        if isinstance(raw, list):
            module_entries = raw
    elif isinstance(lifecycle, list):
        module_entries = lifecycle
    return seed_entries, module_entries


def check_lifecycle_attribution(
    data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """CHG-L015: lifecycle-entry attribution (flows doc §4, GOV-021).

    Presence guard over the lifecycle-carrying sources (upstream/midstream/
    design, plus spec and reconciliation — same family as CHG-L014): every
    `seed_scope.entries[]` / `module_lifecycle` entry must carry a non-empty
    `author` (AI agent id + supervising human); module entries must also
    carry `chg_ref`. Deterministic half of GOV-021 — carrier completeness on
    the documents themselves stays with the reviewer lens. Other sources pass
    through untouched.
    """
    control = data.get("change_control", {})
    if not isinstance(control, dict):
        control = {}
    source = control.get("change_source")
    if source in (None, "null", ""):
        meta = data.get("metadata", {})
        if isinstance(meta, dict):
            fallback = meta.get("change_source")
            if isinstance(fallback, dict):
                fallback = fallback.get("value", source)
            if fallback not in (None, "null", ""):
                source = fallback

    # Same lifecycle-carrying family as CHG-L014 (#722).
    if source not in ("upstream", "midstream", "design", "spec", "reconciliation"):
        passes.append("CHG-L015: non-lifecycle source — attribution guard not applicable")
        return

    seed_entries, module_entries = _lifecycle_entries(data)
    if not seed_entries and not module_entries:
        passes.append("CHG-L015: no lifecycle entries — guard not applicable")
        return

    problems: list[str] = []
    for idx, entry in enumerate(seed_entries):
        if not isinstance(entry, dict) or not entry.get("author"):
            problems.append(f"seed_scope.entries[{idx}] lacks a non-empty `author` (GOV-021)")
    for idx, entry in enumerate(module_entries):
        if not isinstance(entry, dict):
            problems.append(f"module_lifecycle entry[{idx}] is not a mapping (GOV-021)")
            continue
        if not entry.get("author"):
            problems.append(f"module_lifecycle entry[{idx}] lacks a non-empty `author` (GOV-021)")
        if not entry.get("chg_ref"):
            problems.append(f"module_lifecycle entry[{idx}] lacks `chg_ref` (GOV-021)")
    if problems:
        errors.append(
            "CHG-L015: lifecycle entries without AI attribution "
            "(GOV-021) — every seed/module lifecycle entry must name its author; "
            "module entries must also cite chg_ref: " + "; ".join(problems)
        )
        return
    passes.append("CHG-L015: lifecycle entries carry author/chg_ref attribution")


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    sdd_root: Path | None = None
    files: list[str] = []
    i = 0
    while i < len(argv):
        if argv[i] == "--sdd-root":
            if i + 1 >= len(argv):
                print("❌ --sdd-root requires a directory argument", file=sys.stderr)
                return 2
            sdd_root = Path(argv[i + 1])
            if not sdd_root.is_dir():
                print(f"❌ --sdd-root not a directory: {sdd_root}", file=sys.stderr)
                return 2
            i += 2
        else:
            files.append(argv[i])
            i += 1

    if not files:
        print(
            "Usage: chg_lint.py [--sdd-root <dir>] <chg-file.yaml> [chg-file2.yaml ...]",
            file=sys.stderr,
        )
        return 2

    total_errors = 0
    total_warnings = 0

    for arg in files:
        path = Path(arg)
        if not path.exists():
            print(f"❌ File not found: {path}", file=sys.stderr)
            total_errors += 1
            continue

        errors, warnings, passes = lint_chg(path, sdd_root)
        total_errors += len(errors)
        total_warnings += len(warnings)

        print(f"\n{'=' * 60}")
        print(f"CHG Lint: {path.name}")
        print(f"{'=' * 60}")

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

    print(f"\n{'=' * 60}")
    print(f"Summary: {total_errors} error(s), {total_warnings} warning(s)")
    print(f"{'=' * 60}")

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
