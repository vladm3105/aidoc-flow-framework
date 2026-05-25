"""CLI: python -m sdd_doc_lint [--registry PATH] <path> [<path> ...]

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
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    findings = []
    try:
        for arg in args.paths:
            findings.extend(lint_path(Path(arg), registry=args.registry))
    except OSError as exc:
        # Registry not found/readable (e.g. run outside a framework/ project).
        # Exit 2 (not 1) so callers can tell "could not run" from "found errors".
        print(f"sdd-doc-lint: registry unavailable ({exc}); skipping.", file=sys.stderr)
        return 2

    errors = [f for f in findings if f.severity == "error"]
    for f in sorted(findings, key=lambda x: (x.path, x.line, x.code)):
        stream = sys.stderr if f.severity == "error" else sys.stdout
        print(str(f), file=stream)

    if errors:
        print(
            f"\nsdd-doc-lint: {len(errors)} error(s) across {len({f.path for f in errors})} file(s).",
            file=sys.stderr,
        )
        return 1
    print("sdd-doc-lint: no structural findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
