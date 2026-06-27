"""CLI: python -m sdd_doc_lint [--registry PATH] [--mode build|gate-code]
       [--skip-coverage-gate] <path> [<path> ...]

Exit 0 = no error-level findings; 1 = error findings; 2 = usage error.
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

from . import lint_path


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
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    findings = []
    try:
        for arg in args.paths:
            findings.extend(
                lint_path(
                    Path(arg),
                    registry=args.registry,
                    mode=args.mode,
                    skip_coverage=args.skip_coverage_gate,
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

    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
