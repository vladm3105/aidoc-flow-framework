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


ROW_LABEL_RE = re.compile(r"^\**(\d+)\**$")


def table_rows(body: str) -> list[tuple[str, list[str]]]:
    """Every pipe-table data row in ``body``, paired with the label to report it by.

    THE LABEL IS THE TABLE'S OWN ``#`` COLUMN WHERE IT DECLARES ONE, and the 1-based position
    otherwise.

    Reporting the position unconditionally is two numbering systems for one table. A warning
    reading ``ledger row 14`` names the fourteenth data row — and in a plan whose ledger was
    split, that row's ``#`` column says 52. Every in-text "ledger row N" reference an author
    writes uses the ``#`` column, so the gate naming a different row sends a reader to the
    wrong claim. It is harmless while a ledger is contiguous 1..N, which every plan's was until
    one was split, and misleading from that moment on.

    The fallback is deliberate: a table with no ``#`` column has no author-visible numbering to
    honour, so position is the only label available and stays exactly as it was.
    """
    rows: list[tuple[str, list[str]]] = []
    numbered = False  # does the table currently being read declare a `#` column?
    position = 0
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            # Prose or a blank line ends the table. The next one re-derives its own header,
            # so a body holding both a numbered and an unnumbered table labels each correctly.
            numbered = False
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: "):  # separator row
            continue
        if cells and cells[0].lower() in ("#", "no", "no."):  # header row
            numbered = True
            continue
        position += 1
        label = str(position)
        if numbered:
            m = ROW_LABEL_RE.match(cells[0])
            # A `#` column whose cell is not a plain number (a continuation row, a merged
            # cell) falls back to position rather than reporting a label that is not one.
            if m:
                label = m.group(1)
        rows.append((label, cells))
    return rows


def _resolve(rel: str, roots: list[Path]) -> Path | None:
    if Path(rel).is_absolute():
        return None  # absolute citations are rejected by the caller, not resolved
    for base in roots:
        # resolve() before the containment check so `..` segments and symlinks
        # are judged by where they land, not by how they are spelled: `sub/../x`
        # inside the root still resolves; anything landing outside does not.
        target = (base / rel).resolve()
        try:
            target.relative_to(base.resolve())
        except ValueError:
            continue
        if target.exists():
            return target
    return None


def check_ledger(
    body: str, roots: list[Path]
) -> tuple[list[str], list[str], list[tuple[str, str, int, int]]]:
    """Return (errors, warnings, drifts).

    The **symbol is authoritative; the line is an advisory hint** (PLAN-051). A symbol at the cited line ±
    PROXIMITY passes silently; a symbol present *elsewhere* in the file passes with a drift **warning** (the
    line is stale — not an error); a genuinely-absent symbol (or an out-of-range line with no symbol to
    anchor on) is an error. ``drifts`` lists ``(symbol, rel, old_line, new_line)`` for **unambiguous** drifts
    (the symbol appears exactly once in the file, so the new line is certain) — consumed by ``--fix``.
    """
    errs: list[str] = []
    warns: list[str] = []
    drifts: list[tuple[str, str, int, int]] = []
    probes: list[tuple[int, str]] = []
    rows = table_rows(body)
    if not rows:
        return ["Claim ledger has no rows"], warns, drifts, probes
    for i, cells in rows:
        citation = cells[-1]
        symbol = cells[-2].strip("`").strip() if len(cells) >= 2 else ""
        if not citation or "UNVERIFIED" in citation.upper():
            errs.append(f"ledger row {i}: UNVERIFIED or missing citation")
            continue
        # PROBE — a claim that CANNOT be settled from source (a live API
        # behaviour, a server-side setting, a runtime observation). Before this
        # state existed the only options were to guess in prose or to stall the
        # plan forever, and authors guessed: one plan answered the same
        # unmeasurable question three different ways across three review passes.
        #
        # A probe is NOT a free pass. It must carry the command that would settle
        # it, and its claim text must say what it BLOCKS — otherwise "PROBE"
        # becomes a way to dodge a citation you simply did not look up.
        if citation.upper().startswith("PROBE"):
            if len(cells) < 2:
                errs.append(
                    f"ledger row {i}: PROBE row needs claim + citation cells — "
                    f"write '| <claim> — blocks Phase <N> | `n/a` | PROBE: <command> |'"
                )
                continue
            cmd = citation.split(":", 1)[1].strip() if ":" in citation else ""
            if not cmd:
                errs.append(
                    f"ledger row {i}: PROBE without a command — write "
                    f"'PROBE: <the command that settles it>'"
                )
            if "block" not in cells[1].lower():
                errs.append(
                    f"ledger row {i}: PROBE claim does not say what it BLOCKS — "
                    f"an unmeasured claim must name the phase it gates, or it "
                    f"reads as merely unfinished"
                )
            # Capture the token it claims to block, so the caller can verify
            # that phase actually EXISTS. A probe whose phase was deleted out
            # from under it blocks nothing — measured on this rule's own first
            # use, where a scope cut removed the named phase and the probe was
            # left pointing at empty space.
            m_blk = re.search(
                r"blocks?\s+\**\s*(Phase\s+[A-Z]\b|[A-Z]\d+[a-z]?\b)", cells[1], re.I
            )
            probes.append((i, m_blk.group(1).strip() if m_blk else ""))
            continue
        m = CITATION_RE.search(citation)
        if not m:
            errs.append(f"ledger row {i}: citation '{citation}' is not path:line")
            continue
        rel, line = m.group(1), int(m.group(2))
        if Path(rel).is_absolute():
            errs.append(
                f"ledger row {i}: citation '{rel}' is absolute — cite paths "
                f"relative to a root"
            )
            continue
        target = _resolve(rel, roots)
        if target is None:
            where = ", ".join(str(r) for r in roots)
            errs.append(
                f"ledger row {i}: path '{rel}' does not exist under any root ({where})"
            )
            continue
        if (
            not target.is_file()
        ):  # directory/symlink-to-dir → fail, never crash on read_text
            errs.append(f"ledger row {i}: path '{rel}' is not a file")
            continue
        lines = target.read_text(errors="replace").splitlines()
        in_range = 1 <= line <= len(lines)
        if not symbol:  # no symbol to anchor on → the line is the only check
            if not in_range:
                errs.append(
                    f"ledger row {i}: line {line} out of range for {rel} ({len(lines)} lines) and no symbol to anchor"
                )
            continue
        window = (
            (chr(10)).join(
                lines[max(0, line - 1 - PROXIMITY) : line - 1 + PROXIMITY + 1]
            )
            if in_range
            else ""
        )
        if symbol in window:
            continue  # precise — the symbol is at (±PROXIMITY of) the cited line
        # the line drifted (or is out of range): the symbol is authoritative — find it anywhere in the file
        hits = [n for n, ln in enumerate(lines, 1) if symbol in ln]
        if not hits:
            errs.append(f"ledger row {i}: symbol '{symbol}' not found in {rel}")
            continue
        nearest = min(hits, key=lambda n: abs(n - line))
        warns.append(
            f"ledger row {i}: symbol '{symbol}' is at {rel}:{nearest} (cited :{line}) — line drifted; citation passes"
        )
        if len(hits) == 1:  # unambiguous → --fix can re-point it
            drifts.append((symbol, rel, line, hits[0]))
    return errs, warns, drifts, probes


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
        errs.append(
            "final Pass does not state a zero-findings result (e.g. 'no new findings' or '**Result:** ready')"
        )
    return errs


def check_plan(
    path: Path, extra_roots: list[Path]
) -> tuple[
    list[str], list[str], list[tuple[str, str, int, int]], dict[str, int | bool]
]:
    """Return (errors, warnings, drifts, info). info: {gated, citations, passes}. Only ``errors`` decide the
    exit code; ``warnings`` are drift notices (never fail); ``drifts`` are the unambiguous re-points for --fix."""
    text = path.read_text(errors="replace")
    secs = sections(text)
    info: dict[str, int | bool] = {"gated": False, "citations": 0, "passes": 0}
    warns: list[str] = []
    drifts: list[tuple[str, str, int, int]] = []
    if "claim ledger" not in secs and "review log" not in secs:
        return [], warns, drifts, info  # not a gated plan; skip
    info["gated"] = True
    roots = [repo_root(path), *extra_roots]
    errs: list[str] = []
    if "claim ledger" not in secs:
        errs.append("missing '## Claim ledger' section")
    else:
        info["citations"] = len(table_rows(secs["claim ledger"]))
        e, w, d, probes = check_ledger(secs["claim ledger"], roots)
        errs += e
        warns += w
        drifts += d
        info["probes"] = len(probes)
        # A PROBE is admissible because it blocks a NAMED phase rather than the
        # plan. That only holds while the phase exists: a scope cut can delete
        # it and leave the probe attached to nothing, which reads as instrumented
        # while blocking no work. Verify the token resolves somewhere in the plan
        # outside the ledger row that names it.
        body_wo_ledger = text.replace(secs["claim ledger"], "")
        for row, blocked in probes:
            if not blocked:
                continue
            if not re.search(
                r"(?:^|[^A-Za-z0-9])" + re.escape(blocked) + r"(?:[^A-Za-z0-9]|$)",
                body_wo_ledger,
            ):
                errs.append(
                    f"ledger row {row}: PROBE says it blocks '{blocked}', but no "
                    f"such phase exists in the plan — a probe attached to a "
                    f"deleted phase blocks nothing"
                )
    if "review log" not in secs:
        errs.append("missing '## Review log' section")
    else:
        info["passes"] = len(PASS_RE.findall(secs["review log"]))
        errs += check_review(secs["review log"])
    return errs, warns, drifts, info


def apply_fixes(path: Path, drifts: list[tuple[str, str, int, int]]) -> int:
    """Re-point drifted citations **per row** (PLAN-051): on the one plan line that carries both the row's
    `symbol` and its `{rel}:{old}` token, replace `:{old}` → `:{new}` (count=1). Returns the number fixed."""
    lines = path.read_text(errors="replace").splitlines(keepends=True)
    fixed = 0
    for symbol, rel, old, new in drifts:
        # trailing-digit boundary guard so `rel:1` doesn't match inside `rel:10`/`rel:11`
        pat = re.compile(re.escape(f"{rel}:{old}") + r"(?!\d)")
        for idx, ln in enumerate(lines):
            if symbol in ln and pat.search(ln):
                lines[idx] = pat.sub(f"{rel}:{new}", ln, count=1)
                fixed += 1
                break
    if fixed:
        path.write_text("".join(lines))
    return fixed


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
    sep = (
        ""
        if (text.endswith("\n\n") or not text)
        else ("\n" if text.endswith("\n") else "\n\n")
    )
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
    ap.add_argument(
        "--init",
        action="store_true",
        help="scaffold Claim-ledger + Review-log sections into the plan(s)",
    )
    ap.add_argument(
        "--fix",
        action="store_true",
        help="re-point unambiguous drifted citation line numbers in the plan(s)",
    )
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
        errs, warns, drifts, info = check_plan(Path(a), extra_roots)
        if args.fix and drifts:
            n = apply_fixes(Path(a), drifts)
            if n:
                print(f"fix  {a} — re-pointed {n} drifted citation(s)")
        if errs:
            failed = True
            print(f"FAIL {a}")
            for e in errs:
                print(f"  - {e}")
        elif info["gated"]:
            print(
                f"ok   {a} — verified {info['citations']} citation(s)"
                + (f", {info['probes']} probe(s)" if info.get("probes") else "")
                + f", {info['passes']} review pass(es)"
            )
        else:
            print(f"ok   {a} (not a gated plan; skipped)")
        if (
            warns and not args.fix
        ):  # drift notices; --fix already re-pointed the fixable ones
            for w in warns:
                print(f"  warn {a}: {w}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
