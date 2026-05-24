#!/usr/bin/env python3
"""GATE-SPEC — diff-aware automatable checks (CHG-D1).

Enforces the two GATE-SPEC error codes that can only be judged from a change
set (a PR / push diff), not from a static snapshot:

  GATE-SPEC-E005  framework/VERSION must change when any framework/** changes
  GATE-SPEC-E008  CHANGELOG.md must be updated alongside a framework/** change

The record-level checks (E001–E004) are the gate-check skill's / a platform's
record validator's job; the static conformance checks (E006 FRAMEWORK_SPEC_VERSION
match, E007 suite green) are the conformance suite's job. The CI workflow runs
this script *and* the conformance suite together; the human approval half is the
platform's protected-branch review.

This is **engine-agnostic CI tooling**: it lives under tests/ (shared, like the
conformance suite), not under framework/ (which ships no runtime).

Usage:
    python tests/chg/spec_gate.py [--base <ref>]

Base ref resolution: --base, else $GATE_SPEC_BASE, else origin/main. If the base
cannot be resolved (no such ref), the script no-ops (exit 0) and says so — CI
pins an explicit base; locally it is best-effort.

Exit codes: 0 = pass or not-a-spec-change (no framework/** in the diff);
1 = a GATE-SPEC diff-aware check failed; 2 = usage / git error.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Codes this script owns (the diff-aware half of GATE-SPEC). Imported by the
# conformance guard so the script can't drift out of sync with the gate def.
CODES = {
    "GATE-SPEC-E005": "framework/VERSION must bump when framework/** changes",
    "GATE-SPEC-E008": "CHANGELOG.md must be updated alongside a framework/** change",
}


def _git(*args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout.strip()


def _resolve_base(explicit: str | None) -> str | None:
    import os

    candidates = [explicit, os.environ.get("GATE_SPEC_BASE"), "origin/main"]
    for ref in candidates:
        if not ref:
            continue
        code, _ = _git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
        if code == 0:
            return ref
    return None


def changed_files(base: str) -> list[str]:
    # Three-dot: changes on HEAD since the merge-base with `base`.
    code, out = _git("diff", "--name-only", f"{base}...HEAD")
    if code != 0:
        raise RuntimeError(f"git diff against {base!r} failed")
    return [line for line in out.splitlines() if line]


def evaluate(files: list[str]) -> list[str]:
    """Return the list of failing GATE-SPEC codes for this change set."""
    touched_framework = any(f.startswith("framework/") for f in files)
    if not touched_framework:
        return []

    failures = []
    if "framework/VERSION" not in files:
        failures.append("GATE-SPEC-E005")
    if "CHANGELOG.md" not in files:
        failures.append("GATE-SPEC-E008")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GATE-SPEC diff-aware checks (CHG-D1).")
    parser.add_argument(
        "--base", help="Base ref to diff against (else $GATE_SPEC_BASE, else origin/main)."
    )
    args = parser.parse_args(argv)

    base = _resolve_base(args.base)
    if base is None:
        print("GATE-SPEC: no resolvable base ref — skipping diff-aware checks (best-effort).")
        return 0

    try:
        files = changed_files(base)
    except RuntimeError as exc:
        print(f"GATE-SPEC: {exc}", file=sys.stderr)
        return 2

    if not any(f.startswith("framework/") for f in files):
        print(f"GATE-SPEC: no framework/ changes vs {base} — not a spec change, OK.")
        return 0

    failures = evaluate(files)
    if not failures:
        print(f"GATE-SPEC: framework/ change vs {base} — VERSION + CHANGELOG updated, OK.")
        return 0

    print(f"GATE-SPEC: FAIL (framework/ changed vs {base}):", file=sys.stderr)
    for code in failures:
        print(f"  {code}: {CODES[code]}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
