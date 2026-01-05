#!/usr/bin/env python3
"""
Lint for numbering phrasing consistency in AI Dev Flow docs.

Ensures guidance says "starting at `01`" (2+ digits, variable-length) and
flags incorrect phrasing that says "starting at `001`".

Usage:
  python3 lint_numbering_phrasing.py [path] [--fix] [--strict]

Defaults to scanning the ai_dev_flow directory.
"""

import argparse
import os
import re
import sys
from pathlib import Path


INCORRECT_PATTERNS = [
    re.compile(r"starting at\s*`001`", re.IGNORECASE),
]

REPLACEMENTS = {
    "starting at `001`": "starting at `01`",
}


def should_check_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() != ".md":
        return False
    # Skip archived or generated docs if desired later
    return True


def scan_file(path: Path) -> list[tuple[int, str]]:
    issues = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return issues

    for i, line in enumerate(text.splitlines(), start=1):
        for pat in INCORRECT_PATTERNS:
            if pat.search(line):
                issues.append((i, line.rstrip()))
                break

    return issues


def fix_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False

    original = text
    for bad, good in REPLACEMENTS.items():
        text = text.replace(bad, good)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint numbering phrasing (start at `01`, not `001`)")
    parser.add_argument("path", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--fix", action="store_true", help="Auto-fix incorrect phrasing")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any issue")
    args = parser.parse_args()

    root = Path(args.path)
    if root.is_file() and should_check_file(root):
        files = [root]
    else:
        files = [p for p in root.rglob("*.md") if should_check_file(p)]

    total_issues = 0
    fixed_files = 0

    for file in files:
        issues = scan_file(file)
        if issues:
            total_issues += len(issues)
            rel = os.path.relpath(file, root)
            for (ln, line) in issues:
                print(f"{rel}:{ln}: Found incorrect numbering phrase: {line}")
            if args.fix:
                if fix_file(file):
                    fixed_files += 1

    if args.fix and fixed_files:
        print(f"\nAuto-fixed phrasing in {fixed_files} file(s)")

    if total_issues == 0:
        print("Numbering phrasing lint passed (no 'starting at `001`' found)")
        return 0

    if args.strict or not args.fix:
        print(f"\nFound {total_issues} issue(s)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

