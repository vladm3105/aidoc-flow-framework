#!/usr/bin/env python3
"""Bugfix IPLAN Linter — validates scoped bugfix IPLANs (CHG-05, #656/#657).

A bugfix IPLAN repairs a closed plan's output without reopening history:
`parent_iplan` names the closed plan, `source_chg` the authorizing CHG, the
manifest is repair-scoped, and the parent is never touched.

Checks (catalog: framework/governance/LINT_RULES.md):
  BGF-01: Filename matches IPLAN-{NEW}_bugfix_{FIXED}_{slug}.yaml
  BGF-02: NEW_ID is max+1 from the directory listing (never counters)
  BGF-03: iplan_id/doc_id matches the filename stem (§3.4.1 A1/A3)
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


NAME_PAT = re.compile(r"^IPLAN-(\d+)_bugfix_(\d+)_(.+)\.ya?ml$", re.IGNORECASE)
SIBLING_PAT = re.compile(r"^IPLAN-(\d+)(?:[_.].*)?\.ya?ml$", re.IGNORECASE)
TERMINAL_STATUSES = frozenset({"completed", "verified"})
ACTIVE_STATUSES = frozenset({"draft", "approved", "in progress"})

# BGF-04: step-order scan over present keywords only (presence is reviewer's job).
# Word boundaries defeat substring false positives ("fixture", "prefix", "hotfix").
ORDER_PATTERNS = (
    ("fix", re.compile(r"\bfix\b")),
    ("regress", re.compile(r"\bregress\w*\b")),
    ("rollback", re.compile(r"\brollback\b")),
    ("revision", re.compile(r"\brevision\b")),
)

# BGF-05: closed vocabulary — anything else (missing, typo, "DON") fails.
RESOLVED_MARKERS = frozenset({"DONE", "SKIPPED"})


def _load(path: Path) -> Any:
    """Read + parse; never raises. Returns the raw document (None for empty),
    a non-dict as-is, or a dict carrying __io_error__/__parse_error__."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return {"__io_error__": str(e)}
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as e:
        return {"__parse_error__": str(e)}


def _repo_root(start: Path) -> Path | None:
    """Nearest ancestor holding .git (max 6 up); None outside a checkout."""
    node = start.resolve()
    for _ in range(6):
        if (node / ".git").exists():
            return node
        if node.parent == node:
            return None
        node = node.parent
    return None


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
    try:
        entries = list(path.parent.iterdir())
    except OSError as e:
        warnings.append(f"BGF-02: cannot list {path.parent} ({e}) — minter unchecked")
        return
    ids = sorted(
        {
            int(s.group(1))
            for f in entries
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
    seen = 0
    bad = 0
    for key, holder in (("iplan_id", dc), ("doc_id", data)):
        if key not in holder or holder[key] in (None, ""):
            continue
        seen += 1
        if str(holder[key]) != want:
            errors.append(f"BGF-03: {key} '{holder[key]}' does not match filename stem ({want})")
            bad += 1
    if seen == 0:
        warnings.append("BGF-03: neither iplan_id nor doc_id declared — add one matching the stem")
    elif bad == 0:
        passes.append(f"BGF-03: declared IDs match filename stem ({want})")


def check_step_order(data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]) -> None:
    """BGF-04: keyword order across steps in step order, never presence."""
    steps: list[str] = []
    exec_cmds = data.get("execution_commands", {})
    if isinstance(exec_cmds, dict):
        raw_impl = exec_cmds.get("implementation", []) or []
        if not isinstance(raw_impl, list):
            warnings.append("BGF-04: execution_commands.implementation is not a list — order unchecked")
            return
        steps.extend(str(s) for s in raw_impl)
    # NOTE: rollback_procedure steps are deliberately NOT scanned — rollback
    # prose naturally mentions "fix" ("revert the fix"), which is not the FIX
    # phase. Rollback presence/order is owned by BGF-05.
    manifest = data.get("file_manifest", {})
    if isinstance(manifest, dict):
        files = manifest.get("files", []) or []
        if not isinstance(files, list):
            warnings.append("BGF-04: file_manifest.files is not a list — order unchecked")
            return
        for entry in files:
            if isinstance(entry, dict):
                steps.append(str(entry.get("description", "")))
    # (step_index, keyword_index) in step order; the keyword indexes must be
    # non-decreasing for the normative order to hold.
    seq: list[tuple[int, int]] = []
    for i, text in enumerate(steps):
        lowered = text.lower()
        for k, (_, pat) in enumerate(ORDER_PATTERNS):
            if pat.search(lowered):
                seq.append((i, k))
    if len({k for _, k in seq}) < 2:
        passes.append("BGF-04: fewer than two order keywords present — order unchecked")
        return
    keys = [k for _, k in seq]
    if keys != sorted(keys):
        errors.append(
            "BGF-04: step order violated (want fix → regression → rollback → revision entry last): "
            + " → ".join(ORDER_PATTERNS[k][0] for k in keys)
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
    if not isinstance(resolution, list) or not resolution:
        errors.append("BGF-05: rollback resolution note missing — record PENDING→DONE/SKIPPED markers")
        return
    bad = [
        str(r.get("item", "?")) if isinstance(r, dict) else repr(r)
        for r in resolution
        if not isinstance(r, dict) or str(r.get("marker", "")).upper() not in RESOLVED_MARKERS
    ]
    if bad:
        errors.append(
            "BGF-05: rollback marker(s) not DONE/SKIPPED (missing, PENDING, or typo): "
            + ", ".join(bad)
        )
    else:
        passes.append("BGF-05: rollback present, all resolution markers DONE/SKIPPED")


def check_manifest(
    path: Path, data: dict[str, Any], errors: list[str], warnings: list[str], passes: list[str]
) -> None:
    """BGF-06: DONE entries exist on disk (machine half of manifest accuracy)."""
    manifest = data.get("file_manifest", {})
    if not isinstance(manifest, dict):
        warnings.append("BGF-06: file_manifest is not a mapping — nothing to verify on disk")
        return
    files = manifest.get("files", []) or []
    if not isinstance(files, list):
        errors.append("BGF-06: file_manifest.files is not a list")
        return
    if not files:
        warnings.append("BGF-06: empty file_manifest — nothing to verify on disk")
        return
    roots = [path.parent]
    repo = _repo_root(path.parent)
    if repo is not None and repo != path.parent:
        roots.append(repo)
    missing = []
    for entry in files:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("status", "")).strip().upper() != "DONE":
            continue
        rel = str(entry.get("path", "") or "").strip()
        if not rel:
            errors.append("BGF-06: DONE manifest entry without a path")
            continue
        if not any((root / rel).exists() for root in roots):
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
    nn = f"{int(num.group(1)):02d}"
    exact = [path.parent / f"IPLAN-{nn}.yaml", path.parent / f"IPLAN-{nn}.yml"]
    suffixed = list(path.parent.glob(f"IPLAN-{nn}_*.yaml")) + list(path.parent.glob(f"IPLAN-{nn}_*.yml"))
    if not any(p.exists() for p in exact) and not suffixed:
        warnings.append(f"BGF-07: parent file for {target} not found beside the bugfix — originality unchecked")
        return
    originals = [p for p in exact if p.exists()]
    originals += sorted(p for p in suffixed if "_bugfix_" not in p.name)
    if not originals:
        errors.append(
            f"BGF-07: every same-number file for {target} is itself a bugfix — "
            "no fix-on-fix (mint a sibling)"
        )
        return
    candidates = originals
    try:
        parent_doc = yaml.safe_load(candidates[0].read_text(encoding="utf-8"))
    except yaml.YAMLError:
        warnings.append(f"BGF-07: parent file {candidates[0].name} unparsable — originality unchecked")
        return
    if not isinstance(parent_doc, dict):
        warnings.append(f"BGF-07: parent file {candidates[0].name} is not a mapping — unchecked")
        return
    pdc = _doc_control(parent_doc)
    pstatus = str(pdc.get("status", "") or "").strip().casefold()
    if str(pdc.get("subtype", "")).lower() == "bugfix":
        errors.append(f"BGF-07: parent {target} is itself a bugfix — no fix-on-fix (mint a sibling)")
    elif pstatus in ACTIVE_STATUSES:
        errors.append(
            f"BGF-07: parent {target} is still active ({pdc.get('status')}) — "
            "bugfix parents must be terminal (Completed/Verified)"
        )
    elif pstatus not in TERMINAL_STATUSES:
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
    if isinstance(data, dict) and "__io_error__" in data:
        errors.append(f"Cannot read {path}: {data['__io_error__']}")
        return errors, warnings, passes
    if isinstance(data, dict) and "__parse_error__" in data:
        errors.append(f"YAML parse error: {data['__parse_error__']}")
        return errors, warnings, passes
    if data is None:
        errors.append(f"BGF-00: {path.name} is empty — a bugfix IPLAN must declare its repair")
        return errors, warnings, passes
    if not isinstance(data, dict):
        errors.append(f"BGF-00: {path.name} is not a YAML mapping — a bugfix IPLAN must be one")
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
    if any(a in ("-h", "--help") for a in argv):
        print("Usage: bugfix_lint.py [--] <bugfix-iplan.yaml> [bugfix-iplan2.yaml ...]", file=sys.stderr)
        return 2
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    unknown = [a for a in argv if a.startswith("-")]
    if unknown:
        print(f"Unknown option(s): {' '.join(unknown)}", file=sys.stderr)
        print("Usage: bugfix_lint.py [--] <bugfix-iplan.yaml> [bugfix-iplan2.yaml ...]", file=sys.stderr)
        return 2
    files = argv
    if not files:
        print("Usage: bugfix_lint.py [--] <bugfix-iplan.yaml> [bugfix-iplan2.yaml ...]", file=sys.stderr)
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
