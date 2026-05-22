#!/usr/bin/env python3
"""PLM migration gate — flags legacy 12-layer fingerprints in the Claude Code
plugin's skill corpus (see plans/PLM-PLAN.md).

NOT a conformance test (no ``test_`` prefix) so ``unittest discover`` ignores it
while the migration is in flight. B7 promotes the clean-corpus assertion into the
suite.

Model: a *family* is a skill directory with its operation suffix
(-audit/-autopilot/-fixer/-reviewer/-validator) stripped, or a top-level
helper file's base name. The checker FAILS (exit 1) only on fingerprints inside
families listed in ``MIGRATED`` — fingerprints elsewhere are expected until that
family's batch lands, and are reported as an informational remaining count.

Run:  python3 tests/conformance/platforms/plm_lint.py
      python3 tests/conformance/platforms/plm_lint.py --migrated doc-tdd,doc-iplan
      python3 tests/conformance/platforms/plm_lint.py --all   # enforce whole corpus (B7)
"""

import argparse
import re
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3] / "platforms" / "claude-code-plugin"
SKILLS = PLUGIN / "skills"

OP_SUFFIX = re.compile(r"-(audit|autopilot|fixer|reviewer|validator)$")

# Families migrated to the 8-layer model so far. Extend this each batch; the
# checker enforces a zero-fingerprint rule over exactly these families.
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

# Calibrated legacy fingerprints (see PLM-PLAN.md §Verification, dry-run Pass 2).
FINGERPRINTS = {
    "layer-fm(9-12)": re.compile(r"^\s*layer:\s*(9|1[0-2])\b", re.MULTILINE),
    "prose-layer(9-12)": re.compile(r"\bLayer (9|10|11|12)\b|\bL(9|10|11|12)\b"),
    "legacy-path": re.compile(
        r"ai_dev_ssd_flow/|framework/scripts/|\.claude/skills/|"
        r"framework/(ADR|SYS|REQ|CTR|TSPEC|TASKS|\d{2}_[A-Z]+)/"
    ),
    "legacy-family-ref": re.compile(r"doc-(sys|req|ctr|tspec|tasks)\b"),
    "legacy-element-code": re.compile(r"\b(SYS|REQ|CTR|TSPEC|TASKS)\.[0-9]"),
}


def family_of(rel: Path) -> str:
    """Map a path under skills/ to its family key."""
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
    for path in sorted(SKILLS.rglob("*.md")):
        rel = path.relative_to(SKILLS)
        fam = family_of(rel)
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        file_hits = []
        for label, pat in FINGERPRINTS.items():
            for m in pat.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                file_hits.append((rel, line_no, label, m.group(0)))
        if not file_hits:
            continue
        if enforce_all or fam in MIGRATED:
            migrated_hits.extend(file_hits)
        else:
            remaining += 1
    return migrated_hits, remaining


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--migrated", default="",
                    help="comma-separated families to enforce (overrides built-in MIGRATED)")
    ap.add_argument("--all", action="store_true",
                    help="enforce the whole corpus (B7 final gate)")
    args = ap.parse_args()
    if args.migrated:
        MIGRATED.clear()
        MIGRATED.update(f.strip() for f in args.migrated.split(",") if f.strip())

    hits, remaining = scan(args.all)
    scope = "ALL families" if args.all else (
        ", ".join(sorted(MIGRATED)) if MIGRATED else "(none yet)")
    print(f"PLM lint — enforced scope: {scope}")
    print(f"  files with legacy fingerprints outside enforced scope (remaining): {remaining}")
    if hits:
        print(f"  FAIL — {len(hits)} fingerprint(s) in enforced scope:")
        for rel, line_no, label, frag in hits:
            print(f"    skills/{rel}:{line_no}: [{label}] {frag!r}")
        return 1
    print("  OK — enforced scope is clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
