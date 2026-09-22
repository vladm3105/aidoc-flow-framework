#!/usr/bin/env python3
"""Bugfix IPLAN Linter — validates scoped bugfix IPLANs (CHG-05, #656/#657).

A bugfix IPLAN repairs a closed plan's output without reopening history:
`parent_iplan` names the closed plan, `source_chg` the authorizing CHG, the
manifest is repair-scoped, and the parent is never touched.

Checks (catalog: framework/governance/LINT_RULES.md):
  BGF-01: Filename matches IPLAN-{NEW}_bugfix_{FIXED}_{slug}.yaml
  BGF-02: NEW_ID is max+1 from the directory listing (never counters)
  BGF-03: iplan_id/document_id matches the filename stem (§3.4.1 A1/A3)
  BGF-04: Step order fix → regression → rollback → revision entry last
          (order of present keywords, not presence — presence is reviewer's job)
  BGF-05: rollback_procedure present; resolution markers all DONE/SKIPPED
  BGF-06: DONE manifest entries exist on disk (machine half; scope-boundedness
          beyond existence is reviewer-checked)
  BGF-07: Parent is an original terminal IPLAN (never a bugfix, never active)

Usage:
  python sdd_doc_lint/bugfix_lint.py <bugfix-iplan.yaml> [bugfix-iplan2.yaml ...]

Sibling lookup (BGF-02/BGF-07) runs against the target file's own directory.
Exit codes: 0 clean, 1 error(s), 2 usage error, 3 missing prerequisite.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(3)


NAME_PAT = re.compile(r"^IPLAN-(\d+)_bugfix_(\d+)_(.+)\.ya?ml$")
SIBLING_PAT = re.compile(r"^IPLAN-(\d+)[_.].*\.ya?ml$")
TERMINAL_STATUSES = frozenset({"Completed", "Verified"})
ACTIVE_STATUSES = frozenset({"Draft", "Approved", "In Progress"})

# BGF-04: first-occurrence order of present keywords only.
ORDER_KEYWORDS = ("fix", "regress", "rollback", "revision")


def _load(path: Path) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return {"__parse_error__": str(e)}
    return data if isinstance(data, dict) else {}


def _doc_control(data: dict[str, Any]) -> dict[str, Any]:
    dc = data.get("document_control", {})
    return dc if isinstance(dc, dict) else {}


def check_naming(path: Path, errors: list[str], warnings: list[str], passes: list[str]) -> re.Match | None:
    """BGF-01: filename carries the parentage."""
    m = NAME_PAT.match(path.name)
    if not m:
        errors.append(
            f"BGF-01: '{path.name}' does not match IPLAN-{{NEW}}_bugfix_{{FIXED}}_{{slug}}.yaml"
        )
        return None
    passes.append(f"BGF-01: filename carries parentage (NEW={m.group(1)}, FIXED={m.group(2)})")
    return m


def check_minter(path: Path, m: re.Match, errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """BGF-02: NEW_ID is max+1 from the directory listing."""
    ids = sorted(
        {
            int(s.group(1))
            for f in path.parent.iterdir()
            if f.name != path.name and (s := SIBLING_PAT.match(f.name))
        }
    )
    if not ids:
        warnings.append("BGF-02: no sibling IPLAN-NN files — minter unverifiable")
        return
    want = max(ids) + 1
    if int(m.group(1)) != want:
        errors.append(
            f"BGF-02: NEW_ID {m.group(1)} is not max+1 from the directory listing "
            f"(siblings {ids}, want {want:02d})"
        )
    else:
        passes.append(f"BGF-02: NEW_ID is max+1 from the directory listing ({ids})")


def check_id_match(
    path: Path, m: re.Match, data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """BGF-03: declared IDs match the filename stem."""
    dc = _doc_control(data)
    want = f"IPLAN-{int(m.group(1)):02d}"
    bad = 0
    for key, holder in (("iplan_id", dc), ("doc_id", data)):
        if key in holder and holder[key] not in (None, "") and str(holder[key]) != want:
            errors.append(f"BGF-03: {key} '{holder[key]}' does not match filename stem ({want})")
            bad += 1
    if bad == 0:
        passes.append(f"BGF-03: declared IDs match filename stem ({want})")


def check_step_order(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """BGF-04: order of present keywords, never presence."""
    impl: list[str] = []
    exec_cmds = data.get("execution_commands", {})
    if isinstance(exec_cmds, dict):
        for step in exec_cmds.get("implementation", []) or []:
            impl.append(str(step))
    manifest = data.get("file_manifest", {})
    if isinstance(manifest, dict):
        for entry in manifest.get("files", []) or []:
            if isinstance(entry, dict):
                impl.append(str(entry.get("description", "")))
    blob = "\n".join(impl).lower()
    positions = [(kw, blob.find(kw)) for kw in ORDER_KEYWORDS]
    present = [(kw, pos) for kw, pos in positions if pos >= 0]
    if len(present) < 2:
        passes.append("BGF-04: fewer than two order keywords present — order unchecked")
        return
    ordered = sorted(present, key=lambda kv: kv[1])
    want_sorted = sorted(present, key=lambda kv: ORDER_KEYWORDS.index(kv[0]))
    if [kw for kw, _ in ordered] != [kw for kw, _ in want_sorted]:
        errors.append(
            "BGF-04: step order violated (want fix → regression → rollback → revision entry last): "
            + " → ".join(kw for kw, _ in ordered)
        )
    else:
        passes.append("BGF-04: present keywords follow fix → regression → rollback → revision")


def check_rollback(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """BGF-05: rollback present; resolution markers resolved."""
    rb = data.get("rollback_procedure")
    if not isinstance(rb, dict) or not rb.get("steps"):
        errors.append("BGF-05: rollback_procedure with steps is REQUIRED for bugfix IPLANs")
        return
    resolution = rb.get("resolution", []) or []
    if not resolution:
        errors.append("BGF-05: rollback resolution note missing — record PENDING→DONE/SKIPPED markers")
        return
    pending = [
        str(r.get("item", "?"))
        for r in resolution
        if isinstance(r, dict) and str(r.get("marker", "")).upper() == "PENDING"
    ]
    if pending:
        errors.append(f"BGF-05: unresolved PENDING rollback marker(s): {', '.join(pending)}")
    else:
        passes.append("BGF-05: rollback present, all resolution markers DONE/SKIPPED")


def check_manifest(
    path: Path, data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """BGF-06: DONE entries exist on disk (machine half of manifest accuracy)."""
    manifest = data.get("file_manifest", {})
    files = manifest.get("files", []) if isinstance(manifest, dict) else []
    if not files:
        warnings.append("BGF-06: empty file_manifest — nothing to verify on disk")
        return
    missing = []
    for entry in files:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("status", "")).upper() != "DONE":
            continue
        rel = str(entry.get("path", ""))
        if not rel:
            continue
        if not (Path.cwd() / rel).exists() and not (path.parent / rel).exists():
            missing.append(rel)
    if missing:
        errors.append(f"BGF-06: DONE manifest entrie(s) missing on disk: {', '.join(missing)}")
    else:
        passes.append("BGF-06: all DONE manifest entries exist on disk")


def check_parent(
    path: Path, m: re.Match, data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """BGF-07: parent is an original terminal IPLAN."""
    dc = _doc_control(data)
    parent = str(dc.get("parent_iplan", "") or "")
    fixed = f"IPLAN-{int(m.group(2)):02d}"
    if parent and parent != fixed:
        warnings.append(f"BGF-07: parent_iplan '{parent}' disagrees with filename FIXED id ({fixed})")
    target = parent or fixed
    num = re.fullmatch(r"IPLAN-(\d+)", target)
    if not num:
        errors.append(f"BGF-07: parent reference '{target}' is not an IPLAN-NN id")
        return
    candidates = sorted(path.parent.glob(f"IPLAN-{int(num.group(1)):02d}_*.yaml"))
    candidates += sorted(path.parent.glob(f"IPLAN-{int(num.group(1)):02d}_*.yml"))
    if not candidates:
        warnings.append(f"BGF-07: parent file for {target} not found beside the bugfix — originality unchecked")
        return
    try:
        parent_doc = yaml.safe_load(candidates[0].read_text(encoding="utf-8"))
    except yaml.YAMLError:
        warnings.append(f"BGF-07: parent file {candidates[0].name} unparsable — originality unchecked")
        return
    if not isinstance(parent_doc, dict):
        warnings.append(f"BGF-07: parent file {candidates[0].name} is not a mapping — unchecked")
        return
    pdc = _doc_control(parent_doc)
    if str(pdc.get("subtype", "")).lower() == "bugfix":
        errors.append(f"BGF-07: parent {target} is itself a bugfix — no fix-on-fix (mint a sibling)")
    elif str(pdc.get("status", "")) in ACTIVE_STATUSES:
        errors.append(
            f"BGF-07: parent {target} is still active ({pdc.get('status')}) — "
            "bugfix parents must be terminal (Completed/Verified)"
        )
    elif str(pdc.get("status", "")) not in TERMINAL_STATUSES:
        warnings.append(
            f"BGF-07: parent {target} status '{pdc.get('status')}' is not a known "
            "terminal status — verify it is closed"
        )
    else:
        passes.append(f"BGF-07: parent {target} is an original terminal plan ({pdc.get('status')})")


def lint_bugfix(path: Path) -> tuple[list[str], list[str], list[str]]:
    """Lint a single bugfix IPLAN file; return (errors, warnings, passes)."""
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []

    data = _load(path)
    if data is None:
        errors.append(f"File not found or empty: {path}")
        return errors, warnings, passes
    if "__parse_error__" in data:
        errors.append(f"YAML parse error: {data['__parse_error__']}")
        return errors, warnings, passes

    dc = _doc_control(data)
    if str(dc.get("subtype", "")).lower() != "bugfix":
        warnings.append("Not a bugfix-subtype IPLAN — BGF checks apply to subtype: bugfix only")
        return errors, warnings, passes
    if not dc.get("parent_iplan"):
        errors.append("Bugfix IPLAN missing document_control.parent_iplan")
    if not dc.get("source_chg"):
        warnings.append("Bugfix IPLAN missing document_control.source_chg")

    m = check_naming(path, errors, warnings, passes)
    if m is None:
        return errors, warnings, passes
    check_minter(path, m, errors, warnings, passes)
    check_id_match(path, m, data, errors, warnings, passes)
    check_step_order(data, errors, warnings, passes)
    check_rollback(data, errors, warnings, passes)
    check_manifest(path, data, errors, warnings, passes)
    check_parent(path, m, data, errors, warnings, passes)
    return errors, warnings, passes


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    files = [a for a in argv if not a.startswith("-")]
    if not files or any(a in ("-h", "--help") for a in argv):
        print("Usage: bugfix_lint.py <bugfix-iplan.yaml> [bugfix-iplan2.yaml ...]", file=sys.stderr)
        return 2

    total_errors = 0
    total_warnings = 0
    for arg in files:
        path = Path(arg)
        if not path.exists():
            print(f"❌ File not found: {path}", file=sys.stderr)
            total_errors += 1
            continue
        errors, warnings, passes = lint_bugfix(path)
        total_errors += len(errors)
        total_warnings += len(warnings)
        print(f"\n{'='*60}\nBugfix Lint: {path.name}\n{'='*60}")
        for e in errors:
            print(f"  - ❌ {e}")
        for w in warnings:
            print(f"  - ⚠️  {w}")
        for p in passes:
            print(f"  - ✅ {p}")
        if not errors and not warnings:
            print("\n✅ All checks passed")
    print(f"\n{'='*60}\nSummary: {total_errors} error(s), {total_warnings} warning(s)\n{'='*60}")
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
