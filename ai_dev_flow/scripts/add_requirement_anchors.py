#!/usr/bin/env python3
"""
Add HTML anchor tags to requirement IDs in tables.
Converts: | BO-001 | Description |
To:       | <span id="BO-001">BO-001</span> | Description |
"""

import re
from pathlib import Path
from datetime import datetime


def update_revision_history(content, change_description):
    """Add entry to revision history section."""
    history_pattern = r'(## \d+\.\s*Revision History.*?)((?=\n## |\Z))'
    history_match = re.search(history_pattern, content, re.MULTILINE | re.DOTALL)

    if not history_match:
        return content

    history_section = history_match.group(1)
    rest_of_doc = content[history_match.end():]
    before_history = content[:history_match.start()]

    table_pattern = r'(\| Version \| Date.*?\n\|[-\s|]+\n)((?:\|.*?\n)*)'
    table_match = re.search(table_pattern, history_section, re.MULTILINE)

    if table_match:
        rows = table_match.group(2).strip().split('\n')
        if rows and rows[0].strip():
            version_match = re.match(r'\|\s*(\d+\.\d+)', rows[0])
            if version_match:
                current_version = version_match.group(1)
                major, minor = map(int, current_version.split('.'))
                new_version = f"{major}.{minor + 1}"
            else:
                new_version = "1.1"
        else:
            new_version = "1.1"

        today = datetime.now().strftime("%Y-%m-%d")
        new_row = f"| {new_version} | {today} | {change_description} |\n"

        new_table = table_match.group(1) + new_row + table_match.group(2)
        new_history = history_section[:table_match.start()] + new_table + history_section[table_match.end():]

        return before_history + new_history + rest_of_doc

    return content


def add_anchors_to_requirement_ids(content, req_patterns):
    """
    Add HTML anchor tags to requirement IDs in table cells.

    Args:
        content: File content
        req_patterns: List of regex patterns for requirement IDs (e.g., 'BO', 'FR', 'NFR')

    Returns:
        Updated content with anchors added
    """
    updated = content
    changes_made = 0

    for prefix in req_patterns:
        # Pattern: | REQ-ID | ... in table cells
        # Match requirement ID at start of table cell (after |)
        pattern = rf'\|\s+({prefix}-\d{{3}})\s+\|'

        # Find all matches
        matches = list(re.finditer(pattern, updated))

        # Process in reverse to maintain string positions
        for match in reversed(matches):
            req_id = match.group(1)

            # Check if already has anchor tag
            start_pos = match.start()
            end_pos = match.end()

            # Look back to see if already wrapped
            check_before = updated[max(0, start_pos-50):start_pos]
            if f'id="{req_id}"' in check_before or f'id=\'{req_id}\'' in check_before:
                continue  # Already has anchor

            # Replace: | REQ-ID | with | <span id="REQ-ID">REQ-ID</span> |
            original_text = match.group(0)
            replacement = f'| <span id="{req_id}">{req_id}</span> |'

            updated = updated[:match.start()] + replacement + updated[match.end():]
            changes_made += 1

    return updated, changes_made


def process_file(file_path, req_patterns, dry_run=False):
    """Process a single file to add anchors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR reading {file_path}: {e}")
        return False, 0

    # Add anchors
    updated, changes_made = add_anchors_to_requirement_ids(content, req_patterns)

    if changes_made == 0:
        return False, 0

    # Update revision history
    updated = update_revision_history(updated, f"Added HTML anchors to {changes_made} requirement IDs for cross-document navigation")

    if not dry_run:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated)
            return True, changes_made
        except Exception as e:
            print(f"ERROR writing {file_path}: {e}")
            return False, 0
    else:
        return True, changes_made


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Add HTML anchors to requirement IDs')
    parser.add_argument('--file', help='Specific file to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change')

    args = parser.parse_args()

    # Define files and their requirement patterns
    files_to_process = [
        {
            'path': '/opt/data/ibmcp/docs/BRD/BRD-001_ib_stock_options_mcp_server.md',
            'patterns': ['BO', 'FR', 'NFR']  # Business Objectives, Functional, Non-Functional Requirements
        },
        {
            'path': '/opt/data/ibmcp/docs/PRD/PRD-001_ib_mcp_server_mvp.md',
            'patterns': ['BO', 'FR', 'NFR', 'US']  # All requirement types in PRD
        }
    ]

    # Filter if specific file requested
    if args.file:
        files_to_process = [f for f in files_to_process if f['path'] == args.file]

    total_files = 0
    total_anchors = 0

    for file_config in files_to_process:
        file_path = Path(file_config['path'])

        if not file_path.exists():
            print(f"SKIP: {file_path} (not found)")
            continue

        success, count = process_file(file_path, file_config['patterns'], dry_run=args.dry_run)

        if success:
            total_files += 1
            total_anchors += count
            status = "[DRY-RUN] Would add" if args.dry_run else "Added"
            print(f"{status} {count} anchors to: {file_path}")

    print(f"\n{'Would add' if args.dry_run else 'Added'} {total_anchors} anchors to {total_files} files")


if __name__ == '__main__':
    main()
