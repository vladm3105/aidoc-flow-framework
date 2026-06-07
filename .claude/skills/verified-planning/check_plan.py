#!/usr/bin/env python3
"""Gate a PLAN-*.md: Claim-ledger citations must resolve; Review log must be structured.

stdlib only. Exit 0 = ok, 1 = failures (reported on stdout), 2 = usage error.

Usage:
  check_plan.py [--root DIR ...] <PLAN.md> [more...]   # gate the plan(s)
  check_plan.py --init <PLAN.md> [more...]              # scaffold ledger + review sections

--root adds an extra directory to resolve citations against (for cross-repo
claims); citations are tried against the plan's own repo root first, then each
--root in order.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CITATION_RE = re.compile(r"([\w./\-]+):(\d+)(?:-(\d+))?")
PROXIMITY = 3  # lines; tunable window for the symbol check
PASS_RE = re.compile(r"^###\s+Pass\s+(\d+)\b(.*)$", re.MULTILINE)
# A final pass is "green" if it carries any of these. Deliberately forgiving on
# adjectives ("no <anything> findings") plus an explicit Result/Status marker, so
# a genuinely-clean pass is never rejected over wording.
ZERO_FINDINGS_RE = re.compile(
    # bounded adjective list (not "no <anything> findings", which would false-match
    # "no fix for these findings") + an explicit Result/Status marker
    r"\bno (?:new |further |remaining |outstanding |open |load-bearing |additional )?findings\b"
    r"|\bzero findings\b"
    r"|findings:\s*none"
    r"|finds nothing|nothing (?:new|further)\b"
    r"|(?:result|status):\s*\**\s*(?:ready|green|clean|done|no findings)",
    re.IGNORECASE,
)

SNIPPET = Path(__file__).resolve().parent / "PLAN-TEMPLATE.snippet.md"


def repo_root(start: Path) -> Path:
    p = start.resolve()
    for d in (p, *p.parents):
        if (d / ".git").exists():
            return d
    return Path.cwd()


def sections(text: str) -> dict[str, str]:
    """Map level-2 header (lowercased, trimmed) -> body up to the next level-2 header."""
    out: dict[str, str] = {}
    cur = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"##\s+(.*\S)\s*$", line)
        if m and not line.startswith("###"):
            if cur is not None:
                out[cur] = "\n".join(buf)
            cur = m.group(1).strip().lower()
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf)
    return out


def table_rows(body: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: "):  # separator row
            continue
        if cells and cells[0].lower() in ("#", "no", "no."):  # header row
            continue
        rows.append(cells)
    return rows


def _resolve(rel: str, roots: list[Path]) -> Path | None:
    for base in roots:
        target = base / rel
        if target.exists():
            return target
    return None


def check_ledger(body: str, roots: list[Path]) -> list[str]:
    errs: list[str] = []
    rows = table_rows(body)
    if not rows:
        return ["Claim ledger has no rows"]
    for i, cells in enumerate(rows, 1):
        citation = cells[-1]
        symbol = cells[-2].strip("`").strip() if len(cells) >= 2 else ""
        if not citation or "UNVERIFIED" in citation.upper():
            errs.append(f"ledger row {i}: UNVERIFIED or missing citation")
            continue
        m = CITATION_RE.search(citation)
        if not m:
            errs.append(f"ledger row {i}: citation '{citation}' is not path:line")
            continue
        rel, line = m.group(1), int(m.group(2))
        target = _resolve(rel, roots)
        if target is None:
            where = ", ".join(str(r) for r in roots)
            errs.append(f"ledger row {i}: path '{rel}' does not exist under any root ({where})")
            continue
        if not target.is_file():  # directory/symlink-to-dir → fail, never crash on read_text
            errs.append(f"ledger row {i}: path '{rel}' is not a file")
            continue
        lines = target.read_text(errors="replace").splitlines()
        if line < 1 or line > len(lines):
            errs.append(f"ledger row {i}: line {line} out of range for {rel} ({len(lines)} lines)")
            continue
        if symbol and symbol not in (chr(10)).join(lines[max(0, line - 1 - PROXIMITY) : line - 1 + PROXIMITY + 1]):
            errs.append(f"ledger row {i}: symbol '{symbol}' not found within ±{PROXIMITY} lines of {rel}:{line}")
    return errs


def check_review(body: str) -> list[str]:
    errs: list[str] = []
    passes = list(PASS_RE.finditer(body))
    if len(passes) < 2:
        errs.append(f"Review log has {len(passes)} Pass entr(ies); need at least two")
        return errs
    if not re.search(r"independent", body, re.IGNORECASE):
        errs.append("Review log has no pass marked 'independent'")
    # final pass = the last Pass header by document order; its body runs to EOF
    final_body = body[passes[-1].end() :]
    if not ZERO_FINDINGS_RE.search(final_body):
        errs.append("final Pass does not state a zero-findings result (e.g. 'no new findings' or '**Result:** ready')")
    return errs


def check_plan(path: Path, extra_roots: list[Path]) -> tuple[list[str], dict[str, int | bool]]:
    """Return (errors, info). info: {gated, citations, passes}."""
    text = path.read_text(errors="replace")
    secs = sections(text)
    info: dict[str, int | bool] = {"gated": False, "citations": 0, "passes": 0}
    if "claim ledger" not in secs and "review log" not in secs:
        return [], info  # not a gated plan; skip
    info["gated"] = True
    roots = [repo_root(path), *extra_roots]
    errs: list[str] = []
    if "claim ledger" not in secs:
        errs.append("missing '## Claim ledger' section")
    else:
        info["citations"] = len(table_rows(secs["claim ledger"]))
        errs += check_ledger(secs["claim ledger"], roots)
    if "review log" not in secs:
        errs.append("missing '## Review log' section")
    else:
        info["passes"] = len(PASS_RE.findall(secs["review log"]))
        errs += check_review(secs["review log"])
    return errs, info


def _snippet_parts() -> tuple[str, str]:
    """Split the bundled snippet into its Claim-ledger and Review-log halves."""
    text = SNIPPET.read_text()
    idx = text.find("## Review log")
    if idx == -1:  # snippet malformed; treat whole thing as the ledger part
        return text.rstrip(), ""
    return text[:idx].rstrip(), text[idx:].rstrip()


def do_init(path: Path) -> int:
    """Append whichever of the Claim-ledger / Review-log sections the plan lacks.

    Each section is added independently — a plan that already has one keeps it
    (no duplicate header, no loss of existing content).
    """
    text = path.read_text(errors="replace") if path.exists() else ""
    ledger, review = _snippet_parts()
    add = []
    if "## Claim ledger" not in text:
        add.append(ledger)
    if "## Review log" not in text and review:
        add.append(review)
    if not add:
        print(f"ok   {path} (already has Claim ledger + Review log; unchanged)")
        return 0
    sep = "" if (text.endswith("\n\n") or not text) else ("\n" if text.endswith("\n") else "\n\n")
    path.write_text(text + sep + "\n\n".join(add) + "\n")
    which = " + ".join(s.splitlines()[0].lstrip("# ") for s in add)
    print(f"init {path} (scaffolded: {which})")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="check_plan.py", add_help=True)
    ap.add_argument("plans", nargs="*")
    ap.add_argument(
        "--root",
        action="append",
        default=[],
        metavar="DIR",
        help="extra directory to resolve citations against (repeatable)",
    )
    ap.add_argument("--init", action="store_true", help="scaffold Claim-ledger + Review-log sections into the plan(s)")
    args = ap.parse_args(argv)

    if not args.plans:
        ap.print_usage(sys.stderr)
        return 2

    if args.init:
        for a in args.plans:
            do_init(Path(a))
        return 0

    extra_roots = [Path(r) for r in args.root]
    failed = False
    for a in args.plans:
        errs, info = check_plan(Path(a), extra_roots)
        if errs:
            failed = True
            print(f"FAIL {a}")
            for e in errs:
                print(f"  - {e}")
        elif info["gated"]:
            print(f"ok   {a} — verified {info['citations']} citation(s), {info['passes']} review pass(es)")
        else:
            print(f"ok   {a} (not a gated plan; skipped)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
