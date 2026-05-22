#!/usr/bin/env python3
"""PLM migration gate — flags legacy 12-layer fingerprints in the Claude Code
plugin (see plans/PLM-PLAN.md).

The PLM migration is complete; this gate is now enforced corpus-wide by
``tests/conformance/platforms/test_plm_lint.py`` (which calls ``scan(all)``).
The CLI keeps an incremental ``--migrated`` mode for historical/manual use.

Scope: scans ``skills/``, ``agents/``, and ``commands/``. Files under
``skills/`` are grouped into *families* (the skill directory with its
operation suffix -audit/-autopilot/-fixer/-reviewer/-validator stripped, or a
top-level helper file's base name) and gated by ``MIGRATED``; ``agents/`` and
``commands/`` files are always enforced (they have no batch gating).

Known limitations (deliberately not flagged, to avoid false positives on
legitimate Version-History prose): bare "12-layer"/"SYS/REQ/CTR" mentions in
changelog rows, and legacy 3-segment element IDs on *valid* prefixes
(e.g. ``BRD.01.603c``) — the latter also appears as marked negative examples in
``doc-naming``. Structural references (paths, dotted/dash element & doc IDs,
layer-dir tokens, skill names) are what the patterns target.

Run:  python3 tests/conformance/platforms/plm_lint.py
      python3 tests/conformance/platforms/plm_lint.py --migrated doc-tdd,doc-iplan
      python3 tests/conformance/platforms/plm_lint.py --all   # enforce whole corpus
"""

import argparse
import re
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3] / "platforms" / "claude-code-plugin"
SKILLS = PLUGIN / "skills"

# Scan roots: (subdir name, path, always_enforce). skills/ is family-gated;
# agents/ and commands/ were migrated wholesale (B1/B6) and are always enforced.
ROOTS = [
    ("skills", SKILLS, False),
    ("agents", PLUGIN / "agents", True),
    ("commands", PLUGIN / "commands", True),
]

OP_SUFFIX = re.compile(r"-(audit|autopilot|fixer|reviewer|validator)$")

# Families migrated to the 8-layer model (all of them — migration complete).
MIGRATED: set[str] = {
    # PLM-B1
    "doc-tdd", "doc-iplan", "doc-flow", "skill-recommender", "project-init",
    # PLM-B2
    "doc-brd", "doc-prd", "doc-ears",
    # PLM-B3
    "doc-bdd", "doc-adr", "adr-roadmap",
    # PLM-B4
    "doc-spec", "doc-cspec", "doc-dspec", "doc-uxspec", "doc-riskspec", "doc-procspec",
    # PLM-B5
    "doc-utest", "doc-itest", "doc-stest", "doc-ftest", "doc-ptest", "doc-sectest",
}

# Calibrated legacy fingerprints (see PLM-PLAN.md §Verification + the 2026-05-22
# post-migration gap audit, which added the dash-ref and layer-dir patterns).
FINGERPRINTS = {
    "layer-fm(9-12)": re.compile(r"^\s*layer:\s*(9|1[0-2])\b", re.MULTILINE),
    "prose-layer(9-12)": re.compile(r"\bLayer (9|10|11|12)\b|\bL(9|10|11|12)\b"),
    "legacy-path": re.compile(
        r"ai_dev_ssd_flow/|framework/scripts/|\.claude/skills/|"
        r"framework/(ADR|SYS|REQ|CTR|TSPEC|TASKS|\d{2}_[A-Z]+)/"
    ),
    "legacy-family-ref": re.compile(r"doc-(sys|req|ctr|tspec|tasks)\b"),
    "legacy-element-code": re.compile(r"\b(SYS|REQ|CTR|TSPEC|TASKS)\.[0-9]"),
    # Dash-form document refs to deprecated layers (e.g. SYS-002, REQ-001, TSPEC-01).
    "legacy-doc-ref": re.compile(r"\b(SYS|REQ|CTR|TSPEC|TASKS)-\d{2,}\b"),
    # Legacy layer-directory tokens (e.g. 06_SYS, 07_REQ, 10_TSPEC, 11_TASKS).
    "legacy-layer-dir": re.compile(r"\b\d{2}_(SYS|REQ|CTR|TSPEC|TASKS)\b"),
    # Legacy 3-segment element IDs on valid prefixes (e.g. BRD.01.603c) — the
    # 8-layer model uses 4-segment TYPE.NN.SS.xxxx. Matches only when the value
    # parts are digits/hex (literal NN/SS/xxxx placeholders in prose are skipped)
    # and the token is NOT a 4-segment ID. doc-naming is excepted (it shows
    # 3-segment IDs as marked "wrong → right" teaching examples).
    "legacy-3seg-id": re.compile(
        r"\b(BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN)\.\d{1,3}\.[0-9a-fA-F]{3,4}(?![\w.])"
    ),
}

# Documented exceptions: (label, family) pairs to ignore. ``doc-naming`` is the
# ID-format teaching authority, so it legitimately shows 3-segment IDs as
# "wrong → right" examples. (The former ``project-mngt`` dash-ref exception was
# dropped when that skill was parked to ``legacy/`` — see plans/DECISIONS.md
# D-0017; it no longer lives under any scanned scope.)
EXCEPTIONS = {
    ("legacy-3seg-id", "doc-naming"),
}

# A 3-segment ID shown as a "wrong → right" / "reject this" teaching example is
# legitimate; only flag one used as if it were valid. Skip 3-seg matches whose
# line carries a negative marker.
NEG_MARKERS = ("❌", "✗")  # ❌  ✗
NEG_WORDS = re.compile(
    r"legacy|old|reject|wrong|deprecat|3-seg|must be|re-segment|dash doc ref|→",
    re.IGNORECASE,
)


def _is_teaching_example(text: str, start: int, end: int) -> bool:
    ls = text.rfind("\n", 0, start) + 1
    le = text.find("\n", end)
    line = text[ls : le if le != -1 else len(text)]
    return any(mark in line for mark in NEG_MARKERS) or bool(NEG_WORDS.search(line))


def family_of(rel: Path) -> str:
    """Map a path relative to skills/ to its family key."""
    head = rel.parts[0]
    if head.endswith(".md"):  # top-level helper / quickref / readme file
        stem = head[:-3]
        for marker in ("_quickref", "-skills-readme", "-subtype-skills-readme"):
            if stem.endswith(marker):
                return stem[: -len(marker)]
        return stem
    return OP_SUFFIX.sub("", head)  # skill directory


def scan(enforce_all: bool):
    migrated_hits, remaining = [], 0
    for _name, root, always in ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            rel = path.relative_to(root)
            fam = family_of(rel) if root == SKILLS else path.stem
            disp = path.relative_to(PLUGIN)
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue
            file_hits = []
            for label, pat in FINGERPRINTS.items():
                if (label, fam) in EXCEPTIONS:
                    continue
                for m in pat.finditer(text):
                    if label == "legacy-3seg-id" and _is_teaching_example(
                        text, m.start(), m.end()
                    ):
                        continue
                    line_no = text.count("\n", 0, m.start()) + 1
                    file_hits.append((disp, line_no, label, m.group(0)))
            if not file_hits:
                continue
            if enforce_all or always or fam in MIGRATED:
                migrated_hits.extend(file_hits)
            else:
                remaining += 1
    return migrated_hits, remaining


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--migrated", default="",
                    help="comma-separated families to enforce (overrides built-in MIGRATED)")
    ap.add_argument("--all", action="store_true",
                    help="enforce the whole corpus (final gate)")
    args = ap.parse_args()
    if args.migrated:
        MIGRATED.clear()
        MIGRATED.update(f.strip() for f in args.migrated.split(",") if f.strip())

    hits, remaining = scan(args.all)
    scope = "ALL families" if args.all else (
        ", ".join(sorted(MIGRATED)) if MIGRATED else "(none yet)")
    print(f"PLM lint — enforced scope: {scope} (+ agents/, commands/ always)")
    print(f"  files with legacy fingerprints outside enforced scope (remaining): {remaining}")
    if hits:
        print(f"  FAIL — {len(hits)} fingerprint(s) in enforced scope:")
        for disp, line_no, label, frag in hits:
            print(f"    {disp}:{line_no}: [{label}] {frag!r}")
        return 1
    print("  OK — enforced scope is clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
