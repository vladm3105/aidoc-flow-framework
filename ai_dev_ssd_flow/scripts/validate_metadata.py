#!/usr/bin/env python3
"""
Lightweight YAML frontmatter validator for markdown files.

Checks (non-strict by default):
- Presence of YAML frontmatter delimited by '---' at top of file
- Presence of required key: title

Strict mode (--strict) also requires:
- 'tags' key present (array)
- 'custom_fields' mapping present with at least 'document_type'

Usage:
  python3 scripts/validate_metadata.py [base_dir] [--strict]
"""

import argparse
import sys
from pathlib import Path
import re


FRONTMATTER_PATTERN = re.compile(r"^---\n([\s\S]*?)\n---\n", re.MULTILINE)


def parse_args():
    p = argparse.ArgumentParser(description="Validate YAML frontmatter in markdown files")
    p.add_argument("base_dir", nargs="?", default=".", help="Base directory to scan")
    p.add_argument("--strict", action="store_true", help="Enable strict checks")
    return p.parse_args()


def has_key(block: str, key: str) -> bool:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*", re.MULTILINE)
    return bool(pattern.search(block))


def validate_file(md_path: Path, strict: bool):
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[WARNING] META-W001: Could not read {md_path}: {e}")
        return (False, ["read_error"])

    m = FRONTMATTER_PATTERN.match(text)
    if not m:
        print(f"[ERROR] META-E001: Missing YAML frontmatter: {md_path}")
        return (False, ["missing_frontmatter"])

    fm = m.group(1)

    ok = True
    issues = []

    if not has_key(fm, "title"):
        print(f"[ERROR] META-E002: Missing required key 'title' in {md_path}")
        ok = False
        issues.append("missing_title")

    if strict:
        if not has_key(fm, "tags"):
            print(f"[ERROR] META-E003: Missing key 'tags' in {md_path}")
            ok = False
            issues.append("missing_tags")
        if not has_key(fm, "custom_fields"):
            print(f"[ERROR] META-E004: Missing key 'custom_fields' in {md_path}")
            ok = False
            issues.append("missing_custom_fields")
        else:
            # Weak check for document_type inside custom_fields
            if not re.search(r"custom_fields:\s*[\s\S]*?document_type\s*:\s*", fm, re.MULTILINE):
                print(f"[ERROR] META-E005: 'custom_fields.document_type' missing in {md_path}")
                ok = False
                issues.append("missing_document_type")

    return (ok, issues)


def main():
    args = parse_args()
    base = Path(args.base_dir).resolve()

    md_files = sorted(base.rglob("*.md"))
    total = len(md_files)
    failed = 0

    for md in md_files:
        ok, _ = validate_file(md, args.strict)
        if not ok:
            failed += 1

    print(f"[INFO] META-I000: Scanned {total} markdown files; failures: {failed}")

    if args.strict and failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
