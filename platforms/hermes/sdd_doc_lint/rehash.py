"""CLI: python -m sdd_doc_lint.rehash --check <path> [<path> ...]

Model-2 content-hash verifier (PROVISIONAL-IDS-002 Phase 1). Recomputes each
BRD §7 FR element's content hash and reports drift (``IDDRIFT01``) when the
current title/description no longer hashes to the ID's embedded hash.

DELIBERATELY SEPARATE from ``python -m sdd_doc_lint`` (the default structural
lint). This command is opt-in and advisory-only; it is NOT part of the default
gate, so the default lint's output over the example corpus is byte-identical
before and after this feature. It runs only on ``id_state: canonical`` docs; a
``provisional`` doc is exempt.

Exit 0 always for ``--check`` findings (advisory); 2 = usage error. The command
prints one ``IDDRIFT01`` line per drifted element (or a clean message).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import Finding, rehash_check


def _iter_files(paths: list[str]):
    for arg in paths:
        p = Path(arg)
        if p.is_dir():
            yield from sorted(p.rglob("*.md"))
        else:
            yield p


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sdd_doc_lint.rehash")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify BRD §7 FR element IDs against their content hash (advisory)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (text = human-readable; json = single array of findings)",
    )
    parser.add_argument("paths", nargs="+", help="BRD file(s) or directory(ies)")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    if not args.check:
        parser.error("nothing to do: pass --check")

    findings: list[Finding] = []
    for f in _iter_files(args.paths):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"sdd_doc_lint.rehash: cannot read {f} ({exc})", file=sys.stderr)
            return 2
        findings.extend(rehash_check(text, str(f)))

    if args.format == "json":
        import json

        print(
            json.dumps(
                [
                    {
                        "code": x.code,
                        "severity": x.severity,
                        "file": str(x.path),
                        "line": x.line,
                        "message": x.message,
                    }
                    for x in sorted(findings, key=lambda x: (x.path, x.line))
                ]
            )
        )
    else:
        for x in sorted(findings, key=lambda x: (x.path, x.line)):
            print(str(x))
        if not findings:
            print("sdd_doc_lint.rehash: no drift — all canonical §7 FR IDs match.")

    # Advisory: IDDRIFT01 findings do not fail the command.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
