"""CLI: python -m sdd_doc_lint [--registry PATH] [--mode build|gate-code]
       [--skip-coverage-gate] [--warn-exit] <path> [<path> ...]

Exit codes:

* **0** — no error-level findings (and, under ``--warn-exit``, no findings at all)
* **1** — error findings; with ``--warn-exit``, warning findings too
* **2** — usage error, *or* the registry could not be read
* **3** — a runtime prerequisite is missing: Python is below the floor, or PyYAML
  cannot be imported. Raised at package import, before any linting. Kept distinct
  from 2 so a caller can tell "the linter declined to run" from "your document is
  wrong" — see ``sdd_doc_lint.EXIT_MISSING_PREREQUISITE``.

The framework registry is located automatically (upward search for
``framework/registry/LAYER_REGISTRY.yaml``, or ``$SDD_REGISTRY`` / ``--registry``),
so the same code runs from the canonical repo or a vendored platform copy.
Backs the ``on_author`` (advisory) and ``pre_merge`` (blocking) trigger points —
see framework/governance/REVIEW_REMEDIATION_FLOW.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import (
    compute_disabled_skippable,
    find_profile,
    lint_path,
    load_active_layers,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sdd_doc_lint")
    parser.add_argument("paths", nargs="+", help="file(s) or directory(ies) to lint")
    parser.add_argument(
        "--registry",
        type=Path,
        default=None,
        help="path to LAYER_REGISTRY.yaml (else $SDD_REGISTRY or an upward search)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (text = human-readable; json = single array of findings)",
    )
    parser.add_argument(
        "--mode",
        choices=("build", "gate-code"),
        default="build",
        help="forward-coverage severity mode (CFB-PR-2 DD-6): 'build' warns when an "
        "in-scope FR reaches a SPEC but no IPLAN; 'gate-code' blocks it",
    )
    parser.add_argument(
        "--skip-coverage-gate",
        action="store_true",
        help="suppress the forward-coverage gate entirely (CFB-PR-2 DD-9 — the "
        "transient-migration escape hatch)",
    )
    parser.add_argument(
        "--warn-exit",
        action="store_true",
        help="exit 1 when any finding is emitted, not only error-severity ones; the "
        "default contract (0 unless an error) is what CI gates on, so callers that "
        "want to see warnings — the plugin's review hook — opt in here",
    )
    parser.add_argument(
        "--active-layers",
        default=None,
        help="CSV of active layers (overrides `.aidoc/profile.yaml` discovery); a "
        "disabled skippable layer (BDD/ADR) is not demanded downstream "
        "(ACTIVE-LAYERS-CASCADE-001)",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    override = None
    if args.active_layers is not None:
        override = frozenset(x.strip().lower() for x in args.active_layers.split(",") if x.strip())

    findings = []
    try:
        for arg in args.paths:
            path = Path(arg)
            if override is not None:
                active_layers = override
            else:
                profile = find_profile(path)
                active_layers = load_active_layers(profile) if profile else None
            findings.extend(
                lint_path(
                    path,
                    registry=args.registry,
                    mode=args.mode,
                    skip_coverage=args.skip_coverage_gate,
                    disabled_skippable=compute_disabled_skippable(active_layers),
                )
            )
    except OSError as exc:
        print(f"sdd-doc-lint: registry unavailable ({exc}); skipping.", file=sys.stderr)
        return 2

    if args.format == "json":
        import json

        payload = [
            {
                "code": f.code,
                "severity": f.severity,
                "file": str(f.path),
                "line": f.line,
                "section": getattr(f, "section", None),
                "message": f.message,
            }
            for f in sorted(findings, key=lambda x: (x.path, x.line, x.code))
        ]
        print(json.dumps(payload))
    else:
        errors = [f for f in findings if f.severity == "error"]
        for f in sorted(findings, key=lambda x: (x.path, x.line, x.code)):
            stream = sys.stderr if f.severity == "error" else sys.stdout
            print(str(f), file=stream)
        if errors:
            print(
                f"\nsdd-doc-lint: {len(errors)} error(s) across "
                f"{len({f.path for f in errors})} file(s).",
                file=sys.stderr,
            )
        elif not findings:
            print("sdd-doc-lint: no structural findings.")

    if any(f.severity == "error" for f in findings):
        return 1
    # Without this, a warning is emitted and then reported as success, so a
    # caller that speaks only on a non-zero exit can never surface one.
    return 1 if (args.warn_exit and findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
