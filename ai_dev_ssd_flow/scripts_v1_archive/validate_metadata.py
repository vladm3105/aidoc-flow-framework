#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated as of UCX v1.9.0.

Migration: Use `ucx validate brd <path>` instead (includes metadata validation).
Removal: This script will be removed in UCX v2.0.0.

See: /opt/data/docs_flow_framework/UCX/docs/QUICK_START.md

--- Original docstring below ---

Lightweight YAML frontmatter validator for markdown files.

Checks (non-strict by default):
- Presence of YAML frontmatter delimited by '---' at top of file
- Presence of required key: title

Strict mode (--strict) also requires:
- 'tags' key present (array)
- 'custom_fields' mapping present with at least 'document_type'
- For BRD documents: 'deliverable_type' with valid value

BRD-specific checks (strict mode only):
- deliverable_type present in custom_fields
- deliverable_type has valid value: code, document, ux, risk, process
- document_type is 'brd-document' (not 'template')

Usage:
  python3 scripts/validate_metadata.py [base_dir] [--strict]
"""

import warnings

warnings.warn(
    "This script is deprecated. Use 'ucx validate brd <path>' instead. "
    "Will be removed in UCX v2.0.0.",
    DeprecationWarning,
    stacklevel=2
)

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


def get_field_value(block: str, key: str) -> str:
    """Extract value for a field from YAML block."""
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", re.MULTILINE)
    match = pattern.search(block)
    return match.group(1).strip() if match else ""


def is_brd_document(md_path: Path, fm: str) -> bool:
    """Check if this is a BRD document instance (not template or guide)."""
    # Exclude guides, references, and non-instance documents
    exclude_patterns = [
        "README.md",
        "GLOSSARY.md",
        "_GUIDE.md",
        "_RULES.md",
        "_STRATEGY.md",
        "_VALIDATION",
        "_DECISION_GUIDE",
        "_COMMANDS",
        "_WORKFLOW",
        "_EXAMPLES",
        "prompt.md",
        "TEMPLATE.md"
    ]

    filename = md_path.name
    if any(pattern in filename for pattern in exclude_patterns):
        return False

    # Check if in BRD directory structure
    if "01_BRD" not in str(md_path):
        return False

    # Check artifact_type
    artifact_type = get_field_value(fm, "artifact_type")
    if artifact_type == "BRD":
        # Make sure it's not a template
        doc_type = get_field_value(fm, "document_type")
        return doc_type == "brd-document"

    return False


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

            # BRD-specific checks
            if is_brd_document(md_path, fm):
                # Check deliverable_type presence
                if not re.search(r"custom_fields:\s*[\s\S]*?deliverable_type\s*:\s*", fm, re.MULTILINE):
                    print(f"[ERROR] META-E006: 'custom_fields.deliverable_type' missing in BRD document {md_path}")
                    ok = False
                    issues.append("missing_deliverable_type")
                else:
                    # Check deliverable_type value
                    deliverable_type = get_field_value(fm, "deliverable_type")
                    valid_types = ["code", "document", "ux", "risk", "process"]
                    if deliverable_type not in valid_types:
                        print(f"[ERROR] META-E007: Invalid deliverable_type '{deliverable_type}' in {md_path}")
                        print(f"                   Valid values: {', '.join(valid_types)}")
                        ok = False
                        issues.append("invalid_deliverable_type")

                # Check document_type is not 'template' for BRD instances
                doc_type = get_field_value(fm, "document_type")
                if doc_type == "template":
                    print(f"[ERROR] META-E008: BRD instance has document_type 'template' (should be 'brd-document') in {md_path}")
                    ok = False
                    issues.append("wrong_document_type")

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
