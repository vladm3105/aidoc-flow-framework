#!/usr/bin/env python3
"""
Extract traceability tags from source files.

TODO: This script is a placeholder. Implement the following functionality:

1. Tag Extraction:
   - Scan source code, documentation, and test files for @artifact-type tags
   - Extract tags in format @type: TYPE-NN:TYPE.NN.TT.SS or @type: TYPE-NN
   - Support patterns: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @ctr, @spec, @tspec, @tasks

2. Output Modes:
   - JSON output to specified file (--output docs/generated/tags.json)
   - Validate-only mode (--validate-only) - check format without output
   - Type filter (--type REQ) - extract tags for specific artifact type
   - Show upstream (--show-all-upstream) - display cumulative tag chain

3. Directory Scanning:
   - Support multiple source directories (--source src/ docs/ tests/)
   - Recursively scan .py, .md, .yaml, .yml, .feature files
   - Extract tags from docstrings, YAML frontmatter, and markdown sections

Usage:
    python extract_tags.py --source src/ docs/ tests/ --output docs/generated/tags.json
    python extract_tags.py --validate-only
    python extract_tags.py --type REQ --show-all-upstream

See Also:
    - validate_tags_against_docs.py: Validates extracted tags against actual documents
    - generate_traceability_matrix.py: Generates matrices from document metadata

Author: AI-Driven SDD Framework
Version: 0.1.0 (placeholder)
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, List, Set
import json


# Tag patterns for extraction
TAG_PATTERNS = {
    'brd': re.compile(r'@brd:\s*([\w\-\.,\s:]+)'),
    'prd': re.compile(r'@prd:\s*([\w\-\.,\s:]+)'),
    'ears': re.compile(r'@ears:\s*([\w\-\.,\s:]+)'),
    'bdd': re.compile(r'@bdd:\s*([\w\-\.,\s:]+)'),
    'adr': re.compile(r'@adr:\s*([\w\-\.,\s:]+)'),
    'sys': re.compile(r'@sys:\s*([\w\-\.,\s:]+)'),
    'req': re.compile(r'@req:\s*([\w\-\.,\s:]+)'),
    'ctr': re.compile(r'@ctr:\s*([\w\-\.,\s:]+)'),
    'spec': re.compile(r'@spec:\s*([\w\-\.,\s:]+)'),
    'tspec': re.compile(r'@tspec:\s*([\w\-\.,\s:]+)'),
    'tasks': re.compile(r'@tasks:\s*([\w\-\.,\s:]+)'),
}

SUPPORTED_EXTENSIONS = {'.py', '.md', '.yaml', '.yml', '.feature'}


def extract_tags_from_file(filepath: Path) -> Dict[str, List[str]]:
    """Extract all traceability tags from a single file.

    Args:
        filepath: Path to the file to scan

    Returns:
        Dictionary mapping tag types to list of extracted values
    """
    tags = {tag_type: [] for tag_type in TAG_PATTERNS}

    try:
        content = filepath.read_text(encoding='utf-8')
        for tag_type, pattern in TAG_PATTERNS.items():
            matches = pattern.findall(content)
            for match in matches:
                # Split comma-separated values
                values = [v.strip() for v in match.split(',')]
                tags[tag_type].extend(values)
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return tags


def scan_directories(source_dirs: List[str]) -> Dict[str, Dict[str, List[str]]]:
    """Scan source directories for files with traceability tags.

    Args:
        source_dirs: List of directory paths to scan

    Returns:
        Dictionary mapping file paths to their extracted tags
    """
    all_tags = {}

    for source_dir in source_dirs:
        dir_path = Path(source_dir)
        if not dir_path.exists():
            print(f"Warning: Directory not found: {source_dir}", file=sys.stderr)
            continue

        for filepath in dir_path.rglob('*'):
            if filepath.is_file() and filepath.suffix in SUPPORTED_EXTENSIONS:
                file_tags = extract_tags_from_file(filepath)
                # Only include files that have at least one tag
                if any(file_tags.values()):
                    all_tags[str(filepath)] = file_tags

    return all_tags


def validate_tag_format(tags: Dict[str, Dict[str, List[str]]]) -> List[str]:
    """Validate extracted tags have correct format.

    Args:
        tags: Dictionary of file paths to their tags

    Returns:
        List of validation error messages
    """
    errors = []

    # Document-level format: TYPE-NN
    doc_pattern = re.compile(r'^[A-Z]+-\d{2,}$')
    # Element-level format: TYPE.NN.TT.SS or TYPE-NN:TYPE.NN.TT.SS
    element_pattern = re.compile(r'^[A-Z]+\.\d{2,}\.\d{2,}\.\d{2,}$')
    combined_pattern = re.compile(r'^[A-Z]+-\d{2,}:[A-Z]+\.\d{2,}\.\d{2,}\.\d{2,}$')

    doc_level_types = {'adr', 'spec', 'ctr'}  # These use document-level format

    for filepath, file_tags in tags.items():
        for tag_type, values in file_tags.items():
            for value in values:
                if not value:
                    continue

                if tag_type in doc_level_types:
                    if not doc_pattern.match(value):
                        errors.append(f"{filepath}: Invalid {tag_type} tag format: {value} (expected TYPE-NN)")
                else:
                    # Element-level or combined format
                    if not (element_pattern.match(value) or combined_pattern.match(value) or doc_pattern.match(value)):
                        errors.append(f"{filepath}: Invalid {tag_type} tag format: {value}")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description='Extract traceability tags from source files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--source', nargs='+', default=['src/', 'docs/', 'tests/'],
                        help='Source directories to scan')
    parser.add_argument('--output', type=str,
                        help='Output JSON file path')
    parser.add_argument('--validate-only', action='store_true',
                        help='Validate tag format without generating output')
    parser.add_argument('--type', type=str,
                        help='Filter by artifact type (BRD, PRD, REQ, etc.)')
    parser.add_argument('--show-all-upstream', action='store_true',
                        help='Display cumulative tag chain for filtered type')

    args = parser.parse_args()

    print(f"Scanning directories: {', '.join(args.source)}")
    all_tags = scan_directories(args.source)

    print(f"Found {len(all_tags)} files with traceability tags")

    # Validate format
    errors = validate_tag_format(all_tags)
    if errors:
        print(f"\nValidation errors ({len(errors)}):")
        for error in errors[:10]:  # Show first 10
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    if args.validate_only:
        if errors:
            print("\nValidation FAILED")
            return 1
        else:
            print("\nValidation PASSED")
            return 0

    # Filter by type if specified
    if args.type:
        tag_type = args.type.lower()
        filtered_tags = {}
        for filepath, file_tags in all_tags.items():
            if file_tags.get(tag_type):
                filtered_tags[filepath] = file_tags
        all_tags = filtered_tags
        print(f"Filtered to {len(all_tags)} files with @{tag_type} tags")

    # Output results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_tags, f, indent=2)
        print(f"Tags written to: {args.output}")
    else:
        # Print summary to stdout
        tag_counts = {tag_type: 0 for tag_type in TAG_PATTERNS}
        for file_tags in all_tags.values():
            for tag_type, values in file_tags.items():
                tag_counts[tag_type] += len(values)

        print("\nTag counts:")
        for tag_type, count in tag_counts.items():
            if count > 0:
                print(f"  @{tag_type}: {count}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
