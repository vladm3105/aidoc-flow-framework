"""CLI: python -m sdd_doc_lint <path> [<path> ...]

Exit 0 = no error-level findings; 1 = error findings; 2 = usage error.
Run from the repository root (it resolves the framework registry relative to the
package). Intended to back the `on_author` (advisory) and `pre_merge` (blocking)
trigger points — see framework/governance/REVIEW_REMEDIATION_FLOW.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import lint_path


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: python -m sdd_doc_lint <path> [<path> ...]", file=sys.stderr)
        return 2

    findings = []
    for arg in argv:
        findings.extend(lint_path(Path(arg)))

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
