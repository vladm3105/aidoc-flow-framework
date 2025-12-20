#!/usr/bin/env python3
"""
Count Validation for SDD Documents

Validates that stated counts match itemized totals in documents.
Supports auto-fix for count mismatches.

Error Codes:
- COUNT-E001: Count mismatch
- COUNT-W001: Missing count verification
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from error_codes import format_error, calculate_exit_code


def find_count_claims(content: str) -> List[Tuple[int, str, int, int]]:
    """
    Find count claims in content.

    Returns list of (count, item_type, line_number, char_position)
    """
    claims = []

    # Patterns for count claims
    patterns = [
        # "18 requirements", "5 features", "12 acceptance criteria"
        r'\b(\d+)\s+(requirement|feature|item|criterion|criteria|test|endpoint|'
        r'component|step|task|section|point|condition|constraint|use case|'
        r'user stor(?:y|ies)|epic|sprint|milestone|deliverable|'
        r'acceptance criteria|AC|risk|dependency|interface|integration)'
        r's?\b',

        # "Total: 18" or "Count: 5"
        r'(?:Total|Count|Sum):\s*(\d+)\s*(\w+)?',

        # "a total of 18 items"
        r'a total of\s+(\d+)\s+(\w+)',

        # "(18 items)" or "[18 requirements]"
        r'[\(\[]\s*(\d+)\s+(\w+)\s*[\)\]]',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            count = int(match.group(1))
            item_type = match.group(2) if match.lastindex >= 2 and match.group(2) else 'items'
            item_type = item_type.lower() if item_type else 'items'
            line_num = content[:match.start()].count('\n') + 1
            claims.append((count, item_type, line_num, match.start()))

    return claims


def count_list_items(content: str, start_pos: int, max_lines: int = 50) -> int:
    """
    Count items in a list following a position.

    Returns count of bullet points, numbered items, or table rows.
    """
    # Get content after the position
    after_content = content[start_pos:]

    # Find the next section or paragraph break
    section_break = re.search(r'\n##\s|\n\n\n', after_content)
    if section_break:
        after_content = after_content[:section_break.start()]

    # Limit to max_lines
    lines = after_content.split('\n')[:max_lines]
    after_content = '\n'.join(lines)

    # Count bullet points
    bullets = len(re.findall(r'^\s*[-*+]\s+', after_content, re.MULTILINE))

    # Count numbered items
    numbered = len(re.findall(r'^\s*\d+[.)]\s+', after_content, re.MULTILINE))

    # Count table rows (excluding header and separator)
    table_rows = re.findall(r'^\|[^|]+\|', after_content, re.MULTILINE)
    table_count = 0
    for i, row in enumerate(table_rows):
        # Skip header row and separator row
        if i > 1 and '---' not in row:
            table_count += 1

    # Return the maximum count found
    return max(bullets, numbered, table_count)


def find_list_before_claim(content: str, claim_pos: int, max_lines: int = 30) -> int:
    """
    Count items in a list before a position (for "X items above" patterns).

    Returns count of items found.
    """
    before_content = content[:claim_pos]

    # Find the start of the current section
    section_start = before_content.rfind('\n## ')
    if section_start != -1:
        before_content = before_content[section_start:]

    # Count items in this section
    bullets = len(re.findall(r'^\s*[-*+]\s+', before_content, re.MULTILINE))
    numbered = len(re.findall(r'^\s*\d+[.)]\s+', before_content, re.MULTILINE))

    return max(bullets, numbered)


def validate_count(
    content: str,
    count: int,
    item_type: str,
    claim_pos: int
) -> Tuple[bool, int]:
    """
    Validate a count claim against actual items.

    Returns (is_valid, actual_count)
    """
    # Try counting items after the claim
    after_count = count_list_items(content, claim_pos)

    # Try counting items before the claim (for summary statements)
    before_count = find_list_before_claim(content, claim_pos)

    # Use the count that makes more sense
    if after_count > 0 and abs(after_count - count) <= abs(before_count - count):
        actual_count = after_count
    elif before_count > 0:
        actual_count = before_count
    else:
        # Could not find a list to validate against
        return True, 0

    return count == actual_count, actual_count


def validate_counts(
    filepath: str,
    auto_fix: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Validate count claims in a document.

    Args:
        filepath: Path to markdown file
        auto_fix: If True, update incorrect counts

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(filepath)
    modified = False

    # Find count claims
    claims = find_count_claims(content)

    for count, item_type, line_num, char_pos in claims:
        # Skip very small counts (not worth validating)
        if count < 3:
            continue

        is_valid, actual_count = validate_count(content, count, item_type, char_pos)

        if not is_valid and actual_count > 0:
            error_msg = f"{filename}:{line_num}: Claimed {count} {item_type}, found {actual_count}"

            if auto_fix:
                # Find and replace the count in the content
                # Get the specific match text
                match_text = content[char_pos:char_pos+50]
                match = re.search(rf'\b{count}\b', match_text)
                if match:
                    # Replace the count
                    before = content[:char_pos + match.start()]
                    after = content[char_pos + match.end():]
                    content = before + str(actual_count) + after
                    modified = True
                    error_msg += f" [AUTO-FIXED: Updated to {actual_count}]"

            errors.append(format_error("COUNT-E001", error_msg))

    # Check for large lists without count verification
    large_lists = re.finditer(
        r'((?:^\s*[-*+]\s+.+\n){10,})',
        content,
        re.MULTILINE
    )

    for match in large_lists:
        line_num = content[:match.start()].count('\n') + 1
        list_size = match.group(0).count('\n')

        # Check if there's a count claim nearby
        surrounding = content[max(0, match.start()-200):min(len(content), match.end()+200)]
        has_count = bool(re.search(r'\b\d+\s+\w+', surrounding))

        if not has_count:
            warnings.append(format_error(
                "COUNT-W001",
                f"{filename}:{line_num}: Large list ({list_size} items) without stated total"
            ))

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return errors, warnings


def find_markdown_files(directory: str) -> List[str]:
    """Find all markdown files in a directory tree."""
    md_files = []

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                md_files.append(os.path.join(root, filename))

    return md_files


def main():
    parser = argparse.ArgumentParser(
        description="Validate stated counts match itemized totals"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to markdown file or directory to scan"
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Auto-fix count mismatches"
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
        errors, warnings = validate_counts(args.path, args.auto_fix)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    else:
        md_files = find_markdown_files(args.path)

        for filepath in md_files:
            errors, warnings = validate_counts(filepath, args.auto_fix)
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
        print("Count validation passed")

    sys.exit(calculate_exit_code(all_errors, all_warnings, args.strict))


if __name__ == "__main__":
    main()
