"""CLI: python -m sdd_doc_lint.rehash --check <path> [<path> ...]
              python -m sdd_doc_lint.rehash --compute --doc-id NN --section-id SS \
                  --title TITLE [--description DESC] [--length {4,8}]

Model-2 content-hash verifier + generator (PROVISIONAL-IDS-002).

``--check`` recomputes each BRD §7 FR element's content hash and reports drift
(``IDDRIFT01``) when the current title/description no longer hashes to the ID's
embedded hash.

``--compute`` is the **generator** side (#342): it prints the content hash for a
single element so an authoring/fixing surface has something to CALL instead of
being told to compute SHA-256 in-prompt — which no LLM can do reliably, and which
`plans/PROVISIONAL-IDS-002-PLAN.md` had already ruled out. It is layer-agnostic:
the caller supplies the fields, so it is usable wherever the layer's field
extraction is defined (today, BRD §7 — see ``ID_NAMING_STANDARDS.md``).

Both modes go through the single canonical implementation
(``compute_element_hash``), so there is exactly one algorithm in the repo.

DELIBERATELY SEPARATE from ``python -m sdd_doc_lint`` (the default structural
lint). This command is opt-in and advisory-only; it is NOT part of the default
gate, so the default lint's output over the example corpus is byte-identical
before and after this feature. ``--check`` runs only on ``id_state: canonical``
docs; a ``provisional`` doc is exempt.

Exit 0 for ``--check`` findings (advisory) and for a successful ``--compute``;
2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from . import Finding, compute_element_hash, rehash_check

# The hash input uses the element ID's OWN segments, which are numeric:
# `BRD.01.07.a7f3` → doc_id `01`, section_id `07` (ID_NAMING_STANDARDS.md
# "Hash algorithm"; rehash_check splits exactly these out before hashing).
# Accepting `BRD-01` here would silently produce a hash the verifier can never
# match — the failure this whole command exists to prevent — so it is rejected
# with a message that names the right form.
_ID_SEGMENT = re.compile(r"^\d{2,}$")


def _iter_files(paths: list[str]):
    for arg in paths:
        p = Path(arg)
        if p.is_dir():
            yield from sorted(p.rglob("*.md"))
        else:
            yield p


def _run_compute(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    for flag, value in (("--doc-id", args.doc_id), ("--section-id", args.section_id)):
        if not _ID_SEGMENT.match(value or ""):
            parser.error(
                f"{flag}: expected the element ID's numeric segment (e.g. 01), got {value!r}. "
                "The hash input is "
                '"{doc_id}:{section_id}:{norm(title)}:{norm(description)}" using the ID\'s '
                "OWN segments — for BRD.01.07.a7f3 that is --doc-id 01 --section-id 07, "
                "not the artifact_id (BRD-01). See governance/ID_NAMING_STANDARDS.md."
            )
    full = compute_element_hash(args.doc_id, args.section_id, args.title, args.description)
    print(full[: args.length])
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sdd_doc_lint.rehash")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="verify BRD §7 FR element IDs against their content hash (advisory)",
    )
    mode.add_argument(
        "--compute",
        action="store_true",
        help="print the content hash for one element (the generator; takes no paths)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (text = human-readable; json = single array of findings)",
    )
    # --compute inputs. Kept as explicit flags rather than positionals so a caller
    # cannot transpose doc_id and section_id silently.
    parser.add_argument("--doc-id", help="--compute: the ID's doc segment, e.g. 01")
    parser.add_argument("--section-id", help="--compute: the ID's section segment, e.g. 07")
    parser.add_argument("--title", help="--compute: the element's title, verbatim")
    parser.add_argument(
        "--description",
        default="",
        help="--compute: the element's description, verbatim (default: empty)",
    )
    parser.add_argument(
        "--length",
        type=int,
        choices=(4, 8),
        default=4,
        help="--compute: hash length; 8 is the collision form (default: 4)",
    )
    parser.add_argument("paths", nargs="*", help="--check: BRD file(s) or directory(ies)")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    if args.compute:
        if args.paths:
            parser.error("--compute takes no paths; it hashes the fields you pass it")
        missing = [
            f
            for f, v in (
                ("--doc-id", args.doc_id),
                ("--section-id", args.section_id),
                ("--title", args.title),
            )
            if v is None
        ]
        if missing:
            parser.error(f"--compute requires {', '.join(missing)}")
        return _run_compute(args, parser)

    if not args.check:
        parser.error("nothing to do: pass --check or --compute")
    if not args.paths:
        parser.error("--check requires at least one path")

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
