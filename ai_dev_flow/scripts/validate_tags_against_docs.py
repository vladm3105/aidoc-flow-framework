#!/usr/bin/env python3
"""Validate traceability tags against actual documents.

Usage:
    python validate_tags_against_docs.py --tags docs/generated/tags.json --docs docs/ --strict
"""

import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def load_tags(tags_file: Path) -> Dict:
    """Load extracted tags JSON."""
    try:
        with open(tags_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load tags file: {e}")
        return {}


def build_document_index(docs_dir: Path) -> Dict:
    """Build index of all documents and their requirements.

    Returns:
        {
            'BRD-001': {
                'path': Path('docs/BRD/BRD-001_...md'),
                'requirements': {'FR-001', 'FR-002', 'NFR-010', ...}
            },
            'SPEC-003': {
                'path': Path('docs/SPEC/SPEC-003_...yaml'),
                'requirements': set()
            }
        }
    """
    doc_index = {}
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        print(f"⚠️  Documentation directory not found: {docs_dir}")
        return doc_index

    # Document type directories
    doc_types = ['BRD', 'PRD', 'EARS', 'SYS', 'ADR', 'REQ', 'SPEC', 'CONTRACTS', 'BDD', 'IMPL', 'TASKS']

    # Patterns for extracting requirement IDs from documents
    req_patterns = [
        re.compile(r'\b(FR-\d+)\b'),          # Functional Requirements
        re.compile(r'\b(NFR-\d+)\b'),         # Non-Functional Requirements
        re.compile(r'\b(BO-\d+)\b'),          # Business Objectives
        re.compile(r'\b(PERF-\d+)\b'),        # Performance Requirements
        re.compile(r'\b(SEC-\d+)\b'),         # Security Requirements
        re.compile(r'\b(scenario-[\w\-]+)\b'), # BDD Scenarios
    ]

    for doc_type in doc_types:
        type_dir = docs_path / doc_type
        if not type_dir.exists():
            continue

        # Find all markdown and YAML files
        for doc_file in type_dir.rglob('*'):
            if doc_file.suffix not in {'.md', '.yaml', '.yml', '.feature'}:
                continue

            # Extract document ID from filename
            # E.g., BRD-001_ib_stock_options.md -> BRD-001
            filename = doc_file.stem
            match = re.match(r'([A-Z]+-\d+)', filename)

            if not match:
                continue

            doc_id = match.group(1)

            # Read document content to extract requirement IDs
            try:
                content = doc_file.read_text(encoding='utf-8')
                requirements = set()

                # Extract all requirement IDs
                for pattern in req_patterns:
                    requirements.update(pattern.findall(content))

                doc_index[doc_id] = {
                    'path': doc_file,
                    'requirements': requirements,
                    'type': doc_type
                }

            except Exception as e:
                print(f"⚠️  Failed to read {doc_file}: {e}")

    return doc_index


def validate_document_exists(doc_id: str, doc_index: Dict) -> Tuple[bool, str]:
    """Check if document exists.

    Returns:
        (exists, error_message)
    """
    if doc_id in doc_index:
        return True, ""

    # Provide helpful error message with available documents
    available = sorted([d for d in doc_index.keys() if d.startswith(doc_id.split('-')[0])])
    if available:
        return False, f"Document {doc_id} not found. Available: {', '.join(available[:5])}"
    else:
        doc_type = doc_id.split('-')[0]
        return False, f"Document {doc_id} not found. No {doc_type} documents found in docs/"


def validate_requirement_exists(doc_id: str, req_id: str, doc_index: Dict) -> Tuple[bool, str]:
    """Check if requirement exists in document.

    Returns:
        (exists, error_message)
    """
    if doc_id not in doc_index:
        return False, f"Document {doc_id} not found"

    requirements = doc_index[doc_id]['requirements']

    if not requirements:
        # Document has no requirements extracted (e.g., SPEC files)
        return True, ""

    if req_id in requirements:
        return True, ""

    # Provide helpful error message
    available = sorted(list(requirements))[:10]
    return False, f"Requirement {req_id} not found in {doc_id}. Available: {', '.join(available)}"


def validate_all_tags(tags_data: Dict, doc_index: Dict) -> List[Dict]:
    """Validate all tags and return errors.

    Returns:
        [
            {
                'file': 'src/module.py',
                'line': 15,
                'tag': '@brd: BRD-001:FR-999',
                'error': 'Requirement FR-999 not found in BRD-001'
            }
        ]
    """
    errors = []

    for file_path, data in tags_data.items():
        # Validate each tag type
        for tag_type, refs in data.get('tags', {}).items():
            # Skip impl-status (already validated in extract_tags.py)
            if tag_type == 'impl-status':
                continue

            for ref in refs:
                if isinstance(ref, str):
                    # Single value (impl-status)
                    continue

                doc_id, req_id = ref

                # Validate document exists
                doc_exists, doc_error = validate_document_exists(doc_id, doc_index)
                if not doc_exists:
                    tag_str = f"{doc_id}:{req_id}" if req_id else doc_id
                    line_num = data.get('line_numbers', {}).get(tag_str, 0)
                    errors.append({
                        'file': file_path,
                        'line': line_num,
                        'tag': f"@{tag_type}: {tag_str}",
                        'error': doc_error
                    })
                    continue

                # Validate requirement exists (if specified)
                if req_id:
                    req_exists, req_error = validate_requirement_exists(doc_id, req_id, doc_index)
                    if not req_exists:
                        tag_str = f"{doc_id}:{req_id}"
                        line_num = data.get('line_numbers', {}).get(tag_str, 0)
                        errors.append({
                            'file': file_path,
                            'line': line_num,
                            'tag': f"@{tag_type}: {tag_str}",
                            'error': req_error
                        })

    return errors


def generate_error_report(errors: List[Dict]) -> str:
    """Generate human-readable error report."""
    if not errors:
        return "✅ No validation errors found"

    lines = [
        "",
        "=" * 80,
        f"❌ VALIDATION ERRORS FOUND: {len(errors)}",
        "=" * 80,
        ""
    ]

    # Group errors by file
    errors_by_file = defaultdict(list)
    for error in errors:
        errors_by_file[error['file']].append(error)

    for file_path in sorted(errors_by_file.keys()):
        file_errors = errors_by_file[file_path]
        lines.append(f"📄 {file_path}")

        for i, error in enumerate(file_errors, 1):
            line_num = error.get('line', 0)
            tag = error.get('tag', '')
            error_msg = error.get('error', '')

            lines.append(f"   {i}. Line {line_num}: {tag}")
            lines.append(f"      ❌ {error_msg}")

        lines.append("")

    lines.append("=" * 80)

    return "\n".join(lines)


def generate_coverage_report(tags_data: Dict, doc_index: Dict) -> str:
    """Generate coverage metrics report."""
    # Count unique documents referenced
    docs_referenced = set()
    reqs_referenced = set()

    for data in tags_data.values():
        for tag_type, refs in data.get('tags', {}).items():
            if tag_type == 'impl-status':
                continue

            for ref in refs:
                if isinstance(ref, str):
                    continue

                doc_id, req_id = ref
                docs_referenced.add(doc_id)
                if req_id:
                    reqs_referenced.add(f"{doc_id}:{req_id}")

    # Count total requirements in documents
    total_reqs = 0
    for doc_info in doc_index.values():
        total_reqs += len(doc_info['requirements'])

    # Calculate coverage
    files_with_tags = sum(1 for data in tags_data.values() if data.get('tags'))
    total_files = len(tags_data)

    lines = [
        "",
        "=" * 80,
        "✓ COVERAGE METRICS",
        "=" * 80,
        "",
        f"Documents Available: {len(doc_index)}",
        f"Documents Referenced: {len(docs_referenced)}",
        f"Coverage: {len(docs_referenced) / len(doc_index) * 100:.1f}%" if doc_index else "N/A",
        "",
        f"Total Requirements (in docs): {total_reqs}",
        f"Requirements Referenced: {len(reqs_referenced)}",
        f"Coverage: {len(reqs_referenced) / total_reqs * 100:.1f}%" if total_reqs else "N/A",
        "",
        f"Files Scanned: {total_files}",
        f"Files with Tags: {files_with_tags}",
        f"Coverage: {files_with_tags / total_files * 100:.1f}%" if total_files else "N/A",
        "",
        "=" * 80
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Validate traceability tags against actual documents'
    )
    parser.add_argument(
        '--tags',
        help='Extracted tags JSON file (or use extract inline)'
    )
    parser.add_argument(
        '--docs',
        default='docs/',
        help='Documentation directory (default: docs/)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Exit with error on validation failure'
    )
    parser.add_argument(
        '--source',
        nargs='+',
        help='Source directories to scan (if --tags not provided)'
    )

    args = parser.parse_args()

    # Load or extract tags
    if args.tags:
        tags_file = Path(args.tags)
        if not tags_file.exists():
            print(f"❌ Tags file not found: {args.tags}")
            return 1

        print(f"Loading tags from: {args.tags}")
        tags_data = load_tags(tags_file)
    elif args.source:
        # Extract tags inline
        print(f"Extracting tags from: {', '.join(args.source)}")
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from extract_tags import scan_directory

        source_dirs = [Path(s) for s in args.source]
        tags_data = scan_directory(source_dirs)
    else:
        print("❌ Either --tags or --source must be provided")
        return 1

    # Build document index
    print(f"Building document index from: {args.docs}")
    doc_index = build_document_index(Path(args.docs))
    print(f"✓ Indexed {len(doc_index)} documents")

    # Validate tags
    print("Validating tags against documents...")
    errors = validate_all_tags(tags_data, doc_index)

    # Print results
    print(generate_error_report(errors))
    print(generate_coverage_report(tags_data, doc_index))

    # Return exit code
    if args.strict and errors:
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
