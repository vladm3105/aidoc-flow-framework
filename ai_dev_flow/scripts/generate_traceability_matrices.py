#!/usr/bin/env python3
"""Generate bidirectional traceability matrices from tags.

Usage:
    python generate_traceability_matrices.py --tags docs/generated/tags.json --output docs/generated/matrices/
    python generate_traceability_matrices.py --auto  # Extract, validate, generate in one step
"""

import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from datetime import datetime


def load_tags(tags_file: Path) -> Dict:
    """Load extracted tags JSON."""
    try:
        with open(tags_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load tags file: {e}")
        return {}


def build_forward_matrix(tags_data: Dict, doc_type: str) -> Dict:
    """Build requirement -> files mapping.

    Args:
        tags_data: Extracted tags data
        doc_type: Document type (BRD, SYS, etc.)

    Returns:
        {
            'BRD-001:FR-001': [
                {'file': 'src/module.py', 'line': 15, 'status': 'complete'}
            ]
        }
    """
    matrix = defaultdict(list)
    tag_type = doc_type.lower()

    for file_path, data in tags_data.items():
        tags = data.get('tags', {})
        line_numbers = data.get('line_numbers', {})

        if tag_type not in tags:
            continue

        # Get implementation status
        status = 'unknown'
        if 'impl-status' in tags and tags['impl-status']:
            status = tags['impl-status'][0]

        # Process each reference
        for doc_id, req_id in tags[tag_type]:
            if req_id:
                key = f"{doc_id}:{req_id}"
            else:
                key = doc_id

            line_num = line_numbers.get(key, 0)

            matrix[key].append({
                'file': file_path,
                'line': line_num,
                'status': status
            })

    return dict(matrix)


def build_reverse_matrix(tags_data: Dict) -> Dict:
    """Build file -> requirements mapping.

    Returns:
        {
            'src/module.py': {
                'brd': ['BRD-001:FR-001', 'BRD-001:FR-002'],
                'sys': ['SYS-001'],
                'spec': ['SPEC-001'],
                'test': ['BDD-001:scenario-1'],
                'status': 'complete'
            }
        }
    """
    matrix = {}

    for file_path, data in tags_data.items():
        tags = data.get('tags', {})

        if not tags:
            continue

        file_tags = {}

        for tag_type, refs in tags.items():
            if tag_type == 'impl-status':
                file_tags['status'] = refs[0] if refs else 'unknown'
                continue

            # Convert refs to strings
            tag_list = []
            for ref in refs:
                if isinstance(ref, str):
                    tag_list.append(ref)
                else:
                    doc_id, req_id = ref
                    if req_id:
                        tag_list.append(f"{doc_id}:{req_id}")
                    else:
                        tag_list.append(doc_id)

            if tag_list:
                file_tags[tag_type] = tag_list

        if file_tags:
            matrix[file_path] = file_tags

    return matrix


def generate_forward_markdown(matrix: Dict, doc_type: str, output_path: Path, tags_data: Dict):
    """Generate forward traceability matrix markdown."""
    lines = [
        f"# {doc_type} Forward Traceability Matrix",
        f"## Requirements → Implementing Code",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Source Files Scanned:** {len(tags_data)}",
        f"**Requirements Tracked:** {len(matrix)}",
        "",
        "---",
        "",
        "| Requirement | Implementing Files | Status | Line |",
        "|-------------|-------------------|--------|------|"
    ]

    # Sort by requirement ID
    for req_id in sorted(matrix.keys()):
        impls = matrix[req_id]

        for impl in impls:
            file_path = impl['file']
            line_num = impl['line']
            status = impl['status']

            # Status emoji
            status_emoji = {
                'complete': '✓',
                'in-progress': '⚠️',
                'pending': '⏳',
                'deprecated': '❌'
            }.get(status, '?')

            lines.append(
                f"| {req_id} | {file_path} | {status_emoji} {status.title()} | {line_num} |"
            )

    lines.extend([
        "",
        "---",
        "",
        "**Note:** This matrix is AUTO-GENERATED from code tag scanning. Do not edit manually.",
        f"**Regenerate:** `python scripts/generate_traceability_matrices.py --type {doc_type}`",
        ""
    ])

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✓ Generated: {output_path}")


def generate_reverse_markdown(matrix: Dict, output_path: Path, tags_data: Dict):
    """Generate reverse traceability matrix markdown."""
    lines = [
        "# Code to Requirements Matrix",
        "## Source Files → Requirements",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Files with Tags:** {len(matrix)}",
        f"**Total Files Scanned:** {len(tags_data)}",
        "",
        "---",
        "",
        "| Source File | BRD | SYS | SPEC | Tests | Status |",
        "|-------------|-----|-----|------|-------|--------|"
    ]

    # Sort by file path
    for file_path in sorted(matrix.keys()):
        file_tags = matrix[file_path]

        brd = ', '.join(file_tags.get('brd', []))
        sys = ', '.join(file_tags.get('sys', []))
        spec = ', '.join(file_tags.get('spec', []))
        test = ', '.join(file_tags.get('test', []))
        status = file_tags.get('status', 'unknown')

        # Status emoji
        status_emoji = {
            'complete': '✓',
            'in-progress': '⚠️',
            'pending': '⏳',
            'deprecated': '❌'
        }.get(status, '?')

        lines.append(
            f"| {file_path} | {brd or '-'} | {sys or '-'} | {spec or '-'} | {test or '-'} | {status_emoji} {status.title()} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "**Note:** This matrix is AUTO-GENERATED from code tag scanning. Do not edit manually.",
        "**Regenerate:** `python scripts/generate_traceability_matrices.py --auto`",
        ""
    ])

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✓ Generated: {output_path}")


def generate_coverage_report(tags_data: Dict, output_path: Path):
    """Generate coverage metrics report."""
    # Count stats
    total_files = len(tags_data)
    files_with_tags = sum(1 for data in tags_data.values() if data.get('tags'))

    # Count tags by type
    tag_counts = defaultdict(int)
    status_counts = defaultdict(int)

    for data in tags_data.values():
        for tag_type, refs in data.get('tags', {}).items():
            if tag_type == 'impl-status':
                for status in refs:
                    status_counts[status] += 1
            else:
                tag_counts[tag_type] += len(refs)

    # Calculate coverage percentage
    coverage_pct = (files_with_tags / total_files * 100) if total_files > 0 else 0

    lines = [
        "# Traceability Coverage Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## File Coverage",
        "",
        f"- **Total Files Scanned:** {total_files}",
        f"- **Files with Tags:** {files_with_tags}",
        f"- **Coverage:** {coverage_pct:.1f}%",
        "",
        "## Tag Distribution",
        ""
    ]

    for tag_type in sorted(tag_counts.keys()):
        count = tag_counts[tag_type]
        lines.append(f"- **@{tag_type}:** {count} references")

    lines.extend([
        "",
        "## Implementation Status",
        ""
    ])

    for status in sorted(status_counts.keys()):
        count = status_counts[status]
        emoji = {
            'complete': '✓',
            'in-progress': '⚠️',
            'pending': '⏳',
            'deprecated': '❌'
        }.get(status, '?')
        lines.append(f"- **{emoji} {status.title()}:** {count} files")

    lines.extend([
        "",
        "---",
        "",
        "**Note:** This report is AUTO-GENERATED. Regenerate using:",
        "`python scripts/generate_traceability_matrices.py --auto`",
        ""
    ])

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✓ Generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate bidirectional traceability matrices from tags'
    )
    parser.add_argument(
        '--tags',
        help='Extracted tags JSON file'
    )
    parser.add_argument(
        '--output',
        default='docs/generated/matrices/',
        help='Output directory (default: docs/generated/matrices/)'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto mode: extract + validate + generate'
    )
    parser.add_argument(
        '--type',
        help='Generate for specific doc type only (BRD, SYS, etc.)'
    )
    parser.add_argument(
        '--source',
        nargs='+',
        default=['src/', 'docs/', 'tests/'],
        help='Source directories to scan (default: src/ docs/ tests/)'
    )

    args = parser.parse_args()

    # Auto mode: extract and validate first
    if args.auto:
        print("=" * 60)
        print("AUTO MODE: Extract → Validate → Generate")
        print("=" * 60)
        print()

        # Step 1: Extract tags
        print("Step 1: Extracting tags...")
        tags_file = Path('docs/generated/tags.json')
        tags_file.parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run([
            'python', 'scripts/extract_tags.py',
            '--source'] + args.source + [
            '--output', str(tags_file)
        ])

        if result.returncode != 0:
            print("❌ Tag extraction failed")
            return 1

        # Step 2: Validate tags
        print("\nStep 2: Validating tags...")
        result = subprocess.run([
            'python', 'scripts/validate_tags_against_docs.py',
            '--tags', str(tags_file),
            '--strict'
        ])

        if result.returncode != 0:
            print("⚠️  Validation found issues (continuing with matrix generation)")

        # Continue with matrix generation
        args.tags = str(tags_file)
        print("\nStep 3: Generating matrices...")

    # Load tags
    if not args.tags:
        print("❌ Either --tags or --auto must be specified")
        return 1

    tags_file = Path(args.tags)
    if not tags_file.exists():
        print(f"❌ Tags file not found: {args.tags}")
        return 1

    print(f"Loading tags from: {args.tags}")
    tags_data = load_tags(tags_file)

    if not tags_data:
        print("❌ No tags found")
        return 1

    output_dir = Path(args.output)

    # Generate matrices for specific type or all types
    doc_types = [args.type.upper()] if args.type else ['BRD', 'PRD', 'SYS', 'EARS', 'ADR', 'REQ', 'SPEC']

    for doc_type in doc_types:
        forward_matrix = build_forward_matrix(tags_data, doc_type)

        if forward_matrix:
            output_path = output_dir / f"{doc_type}_FORWARD_MATRIX.md"
            generate_forward_markdown(forward_matrix, doc_type, output_path, tags_data)

    # Generate reverse matrix
    reverse_matrix = build_reverse_matrix(tags_data)
    if reverse_matrix:
        output_path = output_dir / "CODE_TO_REQUIREMENTS_MATRIX.md"
        generate_reverse_markdown(reverse_matrix, output_path, tags_data)

    # Generate coverage report
    coverage_path = output_dir / "COVERAGE_REPORT.md"
    generate_coverage_report(tags_data, coverage_path)

    print("\n✅ Matrix generation complete!")
    print(f"   Output directory: {output_dir}")

    return 0


if __name__ == '__main__':
    exit(main())
