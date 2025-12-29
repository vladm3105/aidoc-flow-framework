#!/usr/bin/env python3
"""
Section Count Validator for SDD Documents

Validates that section file counts match metadata declarations.
Supports auto-fix for section count mismatches.

Error Codes:
- SEC-E001: Section count mismatch
- SEC-E002: Missing section file
- SEC-E003: Missing Section 0 file
- SEC-W001: Section file gap detected
"""

import argparse
import glob
import os
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from error_codes import format_error, calculate_exit_code


def parse_frontmatter(content: str) -> Optional[Dict]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None


def get_document_prefix(filepath: str) -> Optional[str]:
    """Extract document prefix (e.g., PRD-001) from filename."""
    filename = os.path.basename(filepath)
    # Match patterns like PRD-001.0_, BRD-02.1_, etc.
    match = re.match(r'^([A-Z]+-\d+)\.\d+_', filename)
    if match:
        return match.group(1)
    return None


def find_section_files(directory: str, doc_prefix: str) -> Dict[int, str]:
    """Find all section files for a document and return section number -> filepath mapping."""
    pattern = os.path.join(directory, f"{doc_prefix}.*_*.md")
    files = glob.glob(pattern)

    section_map = {}
    for filepath in files:
        filename = os.path.basename(filepath)
        # Extract section number from filename like PRD-001.5_section_name.md
        match = re.match(rf'^{re.escape(doc_prefix)}\.(\d+)_', filename)
        if match:
            section_num = int(match.group(1))
            section_map[section_num] = filepath

    return section_map


def validate_section_count(
    section0_path: str,
    auto_fix: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Validate section count for a sectioned document.

    Args:
        section0_path: Path to Section 0 file
        auto_fix: If True, update total_sections metadata

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    if not os.path.exists(section0_path):
        errors.append(format_error("SEC-E003", section0_path))
        return errors, warnings

    # Read Section 0 content
    with open(section0_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse frontmatter
    frontmatter = parse_frontmatter(content)
    if not frontmatter:
        errors.append(format_error("VAL-E002", f"{section0_path}: Missing or invalid frontmatter"))
        return errors, warnings

    # Get declared total_sections
    declared_total = frontmatter.get('total_sections')
    if declared_total is None:
        errors.append(format_error("SEC-E001", f"{section0_path}: Missing total_sections field"))
        return errors, warnings

    # Get document prefix
    doc_prefix = get_document_prefix(section0_path)
    if not doc_prefix:
        errors.append(format_error("VAL-E003", f"{section0_path}: Cannot determine document prefix"))
        return errors, warnings

    # Find all section files
    directory = os.path.dirname(section0_path)
    section_map = find_section_files(directory, doc_prefix)

    # Actual section count (excluding Section 0)
    actual_sections = [n for n in section_map.keys() if n > 0]
    actual_count = len(actual_sections)

    # Check for count mismatch
    if declared_total != actual_count:
        error_msg = f"{section0_path}: Declared {declared_total}, found {actual_count}"

        if auto_fix:
            # Update the frontmatter
            new_content = re.sub(
                r'(total_sections:\s*)\d+',
                f'\\g<1>{actual_count}',
                content
            )
            with open(section0_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            error_msg += f" [AUTO-FIXED: Updated to {actual_count}]"

        errors.append(format_error("SEC-E001", error_msg))

    # Check for gaps in section sequence
    if actual_sections:
        expected_sections = set(range(1, max(actual_sections) + 1))
        missing_sections = expected_sections - set(actual_sections)

        if missing_sections:
            for missing in sorted(missing_sections):
                warnings.append(format_error(
                    "SEC-W001",
                    f"{doc_prefix}: Gap at Section {missing}"
                ))

    # Check for missing specific sections referenced in Section 0
    # Look for section references in the index
    section_refs = re.findall(r'Section\s+(\d+)', content)
    for ref in section_refs:
        ref_num = int(ref)
        if ref_num > 0 and ref_num not in section_map:
            errors.append(format_error(
                "SEC-E002",
                f"{doc_prefix}: Section {ref_num} referenced but file not found"
            ))

    return errors, warnings


def find_section0_files(directory: str) -> List[str]:
    """Find all Section 0 files in a directory tree."""
    section0_files = []

    for root, _, files in os.walk(directory):
        for filename in files:
            # Match Section 0 files: TYPE-NNN.0_*.md
            if re.match(r'^[A-Z]+-\d+\.0_.*\.md$', filename):
                section0_files.append(os.path.join(root, filename))

    return section0_files


def main():
    parser = argparse.ArgumentParser(
        description="Validate section file counts against metadata"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Section 0 file or directory to scan"
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Auto-fix section count mismatches"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    args = parser.parse_args()

    all_errors = []
    all_warnings = []

    if os.path.isfile(args.path):
        # Validate single Section 0 file
        errors, warnings = validate_section_count(args.path, args.auto_fix)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    else:
        # Find and validate all Section 0 files
        section0_files = find_section0_files(args.path)

        if not section0_files:
            print("No Section 0 files found")
            sys.exit(0)

        for section0_path in section0_files:
            errors, warnings = validate_section_count(section0_path, args.auto_fix)
            all_errors.extend(errors)
            all_warnings.extend(warnings)

    # Output results
    for error in all_errors:
        print(error)
    for warning in all_warnings:
        print(warning)

    # Summary
    if all_errors or all_warnings:
        print(f"\nSummary: {len(all_errors)} error(s), {len(all_warnings)} warning(s)")
    else:
        print("Section count validation passed")

    sys.exit(calculate_exit_code(all_errors, all_warnings, args.strict))


if __name__ == "__main__":
    main()
