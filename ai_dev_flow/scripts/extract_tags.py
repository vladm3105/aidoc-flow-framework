#!/usr/bin/env python3
"""Extract traceability tags from source code and documentation.

Usage:
    python extract_tags.py --source src/ docs/ --output docs/generated/tags.json
    python extract_tags.py --type BRD --output docs/BRD/BRD-000_TRACEABILITY_MATRIX.md
    python extract_tags.py --validate-only
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Tag pattern: @tag-type: DOCUMENT-ID:REQUIREMENT-ID, ...
TAG_PATTERN = re.compile(
    r'@(\w+(?:-\w+)?):\s*([\w\-]+(?::[\w\-]+)?(?:\s*,\s*[\w\-]+(?::[\w\-]+)?)*)',
    re.MULTILINE
)

# Valid tag types
VALID_TAG_TYPES = {
    'brd', 'prd', 'ears', 'sys', 'adr', 'req', 'spec', 'impl',
    'contract', 'test', 'impl-status'
}

# Valid implementation status values
VALID_STATUS = {'pending', 'in-progress', 'complete', 'deprecated'}

# File extensions to scan
FILE_EXTENSIONS = {'.py', '.md', '.yaml', '.yml', '.feature'}


def parse_tag_value(tag_value: str) -> List[Tuple[str, Optional[str]]]:
    """Parse tag value into (DOCUMENT-ID, ELEMENT-ID) tuples.

    Args:
        tag_value: "BRD.01.01.30, BRD.01.01.31, SPEC-003"

    Returns:
        [('BRD-01', '01.30'), ('BRD-01', '01.31'), ('SPEC-003', None)]
    """
    refs = []
    for item in tag_value.split(','):
        item = item.strip()
        if not item:
            continue

        if ':' in item:
            parts = item.split(':', 1)
            doc_id = parts[0].strip()
            req_id = parts[1].strip() if len(parts) > 1 else None
            refs.append((doc_id, req_id))
        else:
            # No colon - single document reference
            refs.append((item, None))

    return refs


def extract_tags_from_file(file_path: Path) -> Dict:
    """Extract all @tag: references from a file.

    Returns:
        {
            'tags': {
                'brd': [('BRD-001', '001'), ('BRD-001', '002')],
                'sys': [('SYS-001', None)],
                'spec': [('SPEC-001', None)],
                'test': [('BDD-001', '001')],
                'impl-status': ['complete']
            },
            'line_numbers': {
                'BRD.01.01.01': 15,
                'BRD.01.01.02': 15
            },
            'errors': []
        }
    """
    result = {
        'tags': defaultdict(list),
        'line_numbers': {},
        'errors': []
    }

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result['errors'].append(f"Failed to read file: {e}")
        return result

    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        matches = TAG_PATTERN.findall(line)

        for tag_type, tag_value in matches:
            tag_type = tag_type.lower()

            # Validate tag type
            if tag_type not in VALID_TAG_TYPES:
                result['errors'].append(
                    f"Line {line_num}: Invalid tag type '{tag_type}'. "
                    f"Valid: {VALID_TAG_TYPES}"
                )
                continue

            # Handle implementation status specially
            if tag_type == 'impl-status':
                status = tag_value.strip().lower()
                if status not in VALID_STATUS:
                    result['errors'].append(
                        f"Line {line_num}: Invalid status '{status}'. "
                        f"Valid: {VALID_STATUS}"
                    )
                else:
                    result['tags']['impl-status'].append(status)
                continue

            # Parse namespaced references
            try:
                refs = parse_tag_value(tag_value)
                for doc_id, req_id in refs:
                    result['tags'][tag_type].append((doc_id, req_id))

                    # Store line number
                    if req_id:
                        key = f"{doc_id}:{req_id}"
                    else:
                        key = doc_id
                    result['line_numbers'][key] = line_num

            except Exception as e:
                result['errors'].append(
                    f"Line {line_num}: Failed to parse tag value '{tag_value}': {e}"
                )

    # Convert defaultdict to regular dict for JSON serialization
    result['tags'] = dict(result['tags'])

    return result


def scan_directory(source_dirs: List[Path], file_patterns: List[str] = None) -> Dict:
    """Scan directories for files matching patterns.

    Returns:
        {
            'file_path': {
                'tags': {...},
                'line_numbers': {...},
                'errors': [...]
            }
        }
    """
    if file_patterns is None:
        file_patterns = FILE_EXTENSIONS

    all_tags = {}
    total_files = 0
    total_errors = 0

    for source_dir in source_dirs:
        source_path = Path(source_dir)

        if not source_path.exists():
            print(f"⚠️  Directory not found: {source_dir}")
            continue

        if source_path.is_file():
            # Single file
            files = [source_path]
        else:
            # Directory - scan recursively
            files = []
            for ext in file_patterns:
                files.extend(source_path.rglob(f"*{ext}"))

        for file_path in files:
            if file_path.suffix not in FILE_EXTENSIONS:
                continue

            total_files += 1
            result = extract_tags_from_file(file_path)

            # Only include files with tags or errors
            if result['tags'] or result['errors']:
                all_tags[str(file_path)] = result
                total_errors += len(result['errors'])

    print(f"✓ Scanned {total_files} files")
    if total_errors > 0:
        print(f"❌ Found {total_errors} format errors")

    return all_tags


def validate_tags(tags_data: Dict) -> List[str]:
    """Validate tag format compliance.

    Returns:
        List of error messages
    """
    errors = []

    for file_path, data in tags_data.items():
        # Collect file-specific errors
        if data.get('errors'):
            for error in data['errors']:
                errors.append(f"{file_path}: {error}")

        # Validate namespaced format for requirement tags
        for tag_type in ['brd', 'prd', 'ears', 'sys', 'req']:
            if tag_type in data['tags']:
                for doc_id, req_id in data['tags'][tag_type]:
                    # For multi-requirement documents, require namespace
                    if tag_type in ['brd', 'prd'] and not req_id:
                        errors.append(
                            f"{file_path}: Missing requirement ID for @{tag_type}: {doc_id}. "
                            f"Use format: {tag_type.upper()}-XXX:REQ-ID"
                        )

    return errors


def generate_summary_report(tags_data: Dict) -> str:
    """Generate summary statistics report."""
    total_files = len(tags_data)
    files_with_tags = sum(1 for data in tags_data.values() if data['tags'])
    files_with_errors = sum(1 for data in tags_data.values() if data['errors'])

    # Count tags by type
    tag_counts = defaultdict(int)
    for data in tags_data.values():
        for tag_type, refs in data['tags'].items():
            tag_counts[tag_type] += len(refs)

    report = ["", "=" * 60, "TRACEABILITY TAG EXTRACTION SUMMARY", "=" * 60]
    report.append(f"Files scanned: {total_files}")
    report.append(f"Files with tags: {files_with_tags}")
    report.append(f"Files with errors: {files_with_errors}")
    report.append("")
    report.append("Tags by type:")
    for tag_type in sorted(tag_counts.keys()):
        report.append(f"  @{tag_type}: {tag_counts[tag_type]}")
    report.append("=" * 60)

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description='Extract traceability tags from source code and documentation'
    )
    parser.add_argument(
        '--source',
        nargs='+',
        help='Source directories/files to scan'
    )
    parser.add_argument(
        '--output',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--type',
        help='Filter by document type (BRD, SYS, etc.)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Validate tags without generating output'
    )
    parser.add_argument(
        '--docs',
        default='docs/',
        help='Documentation directory (default: docs/)'
    )

    args = parser.parse_args()

    # Default to current directory if no source specified
    if not args.source:
        args.source = ['.']

    # Convert source paths to Path objects
    source_dirs = [Path(s) for s in args.source]

    # Scan directories
    print(f"Scanning: {', '.join(args.source)}")
    tags_data = scan_directory(source_dirs)

    # Validate tags
    errors = validate_tags(tags_data)

    if errors:
        print(f"\n❌ VALIDATION ERRORS FOUND: {len(errors)}\n")
        for error in errors:
            print(f"  {error}")

        if args.validate_only:
            return 1
    else:
        print("✅ All tags valid")

    # Print summary
    print(generate_summary_report(tags_data))

    # Write output if not validate-only mode
    if not args.validate_only and args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, indent=2)

        print(f"\n✓ Tags exported to: {output_path}")

    # Return exit code
    return 1 if errors else 0


if __name__ == '__main__':
    exit(main())
