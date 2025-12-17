#!/usr/bin/env python3
"""Validate traceability tags against actual documents.

Validates:
- Document and requirement references exist
- Cumulative tagging hierarchy compliance (each layer includes all upstream tags)
- Tag format compliance
- Coverage metrics

Usage:
    python validate_tags_against_docs.py --tags docs/generated/tags.json --docs docs/ --strict
    python validate_tags_against_docs.py --source src/ docs/ tests/ --docs docs/ --validate-cumulative --strict
"""

import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# Cumulative Tagging Hierarchy Definition (16 layers)
LAYER_HIERARCHY = {
    0: {'type': 'Strategy', 'required_tags': [], 'tag_count': 0, 'optional': False},
    1: {'type': 'BRD', 'required_tags': [], 'tag_count': 0, 'optional': False},
    2: {'type': 'PRD', 'required_tags': ['brd'], 'tag_count': 1, 'optional': False},
    3: {'type': 'EARS', 'required_tags': ['brd', 'prd'], 'tag_count': 2, 'optional': False},
    4: {'type': 'BDD', 'required_tags': ['brd', 'prd', 'ears'], 'tag_count': 3, 'optional': False},
    5: {'type': 'ADR', 'required_tags': ['brd', 'prd', 'ears', 'bdd'], 'tag_count': 4, 'optional': False},
    6: {'type': 'SYS', 'required_tags': ['brd', 'prd', 'ears', 'bdd', 'adr'], 'tag_count': 5, 'optional': False},
    7: {'type': 'REQ', 'required_tags': ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys'], 'tag_count': 6, 'optional': False},
    8: {'type': 'IMPL', 'required_tags': ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys', 'req'], 'tag_count': 7, 'optional': True},
    9: {'type': 'CTR', 'required_tags': ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys', 'req', 'impl'], 'tag_count': 8, 'optional': True},
    10: {'type': 'SPEC', 'required_tags': ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys', 'req'], 'tag_count_min': 7, 'tag_count_max': 9, 'optional': False},
    11: {'type': 'TASKS', 'required_tags': ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys', 'req', 'spec'], 'tag_count_min': 8, 'tag_count_max': 10, 'optional': False},
    12: {'type': 'iplan', 'required_tags': ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys', 'req', 'spec', 'tasks'], 'tag_count_min': 9, 'tag_count_max': 11, 'optional': False},
    13: {'type': 'Code', 'required_tags': ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys', 'req', 'spec', 'tasks'], 'tag_count_min': 9, 'tag_count_max': 11, 'optional': False},
    14: {'type': 'Tests', 'required_tags': ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys', 'req', 'spec', 'tasks', 'code'], 'tag_count_min': 10, 'tag_count_max': 12, 'optional': False},
    15: {'type': 'Validation', 'required_tags': [], 'tag_count_min': 10, 'tag_count_max': 15, 'optional': False}
}

# Map artifact types to layers
ARTIFACT_TYPE_TO_LAYER = {
    'brd': 1, 'prd': 2, 'ears': 3, 'bdd': 4, 'adr': 5, 'sys': 6,
    'req': 7, 'impl': 8, 'ctr': 9, 'spec': 10, 'tasks': 11,
    'iplan': 12, 'code': 13, 'tests': 14, 'validation': 15
}


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
                'elements': {'BRD.01.01.01', 'BRD.01.01.02', ...}
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
    doc_types = ['BRD', 'PRD', 'EARS', 'SYS', 'ADR', 'REQ', 'SPEC', 'CTR', 'BDD', 'IMPL', 'TASKS', 'IPLAN']

    # Patterns for extracting requirement IDs from documents
    req_patterns = [
        re.compile(r'\b(FR-\d+)\b'),          # Functional Requirements
        re.compile(r'\b(QA-\d+)\b'),          # Quality Attributes (replaces NFR)
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
                'tag': '@brd: BRD.01.01.99',
                'error': 'Element 99 not found in BRD-01'
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


def detect_artifact_layer(file_path: str, tags: Dict) -> Optional[int]:
    """Detect which layer an artifact belongs to based on file path or tags.

    Returns:
        Layer number (0-15) or None if cannot detect
    """
    # Check file path for artifact type
    path_lower = file_path.lower()

    # Document artifacts
    for artifact_type, layer in ARTIFACT_TYPE_TO_LAYER.items():
        if f"/{artifact_type}/" in path_lower or f"\\{artifact_type}\\" in path_lower:
            return layer

    # Check filename patterns
    filename = Path(file_path).stem.lower()
    for artifact_type in ['brd', 'prd', 'ears', 'bdd', 'adr', 'sys', 'req', 'impl', 'ctr', 'spec', 'tasks']:
        if filename.startswith(artifact_type + '-'):
            return ARTIFACT_TYPE_TO_LAYER[artifact_type]

    # Code files
    if path_lower.endswith(('.py', '.js', '.ts', '.java', '.go')):
        # Check if it's a test file
        if 'test' in filename or path_lower.endswith('_test.py'):
            return 14  # Tests layer
        return 13  # Code layer

    return None


def validate_cumulative_tags(file_path: str, tags: Dict, artifact_layer: int) -> List[Dict]:
    """Validate cumulative tagging compliance for an artifact.

    Checks:
    1. All required upstream tags are present
    2. No gaps in the tag chain
    3. Tag count is within expected range
    4. Optional layers (IMPL, CTR) are handled correctly

    Returns:
        List of validation errors
    """
    errors = []

    if artifact_layer is None or artifact_layer < 2:
        # No upstream tags required for Strategy (0) and BRD (1)
        return errors

    layer_config = LAYER_HIERARCHY.get(artifact_layer)
    if not layer_config:
        return errors

    required_tags = layer_config['required_tags']
    present_tags = set(tags.keys()) - {'impl-status'}

    # Calculate expected tag count (accounting for optional layers)
    if 'tag_count' in layer_config:
        expected_min = expected_max = layer_config['tag_count']
    else:
        expected_min = layer_config['tag_count_min']
        expected_max = layer_config['tag_count_max']

    actual_count = len(present_tags)

    # Check 1: Missing required tags (no gaps allowed)
    missing_tags = set(required_tags) - present_tags

    # Handle optional layers: impl and ctr
    # If impl or ctr are in required_tags but missing, only error if they should exist
    optional_missing = missing_tags & {'impl', 'ctr'}
    mandatory_missing = missing_tags - {'impl', 'ctr'}

    if mandatory_missing:
        errors.append({
            'file': file_path,
            'line': 0,
            'error_type': 'missing_required_tags',
            'error': f"Missing required upstream tags for {layer_config['type']} (Layer {artifact_layer}): {', '.join(sorted(mandatory_missing))}"
        })

    # Check 2: Tag count validation
    if actual_count < expected_min:
        errors.append({
            'file': file_path,
            'line': 0,
            'error_type': 'insufficient_tag_count',
            'error': f"Insufficient tag count for {layer_config['type']} (Layer {artifact_layer}): found {actual_count}, expected {expected_min}-{expected_max}"
        })
    elif actual_count > expected_max:
        errors.append({
            'file': file_path,
            'line': 0,
            'error_type': 'excessive_tag_count',
            'error': f"Excessive tag count for {layer_config['type']} (Layer {artifact_layer}): found {actual_count}, expected {expected_min}-{expected_max}"
        })

    # Check 3: Validate tag chain completeness (no gaps)
    # For example, if @adr exists, @brd, @prd, @ears, @bdd must all exist
    tag_layers = {tag: ARTIFACT_TYPE_TO_LAYER.get(tag, -1) for tag in present_tags}
    max_layer = max(tag_layers.values()) if tag_layers else 0

    for layer_num in range(2, max_layer):
        layer_type = LAYER_HIERARCHY[layer_num]['type'].lower()
        # Skip optional layers in gap check
        if layer_type in {'impl', 'ctr'}:
            continue
        if layer_type not in present_tags:
            errors.append({
                'file': file_path,
                'line': 0,
                'error_type': 'tag_chain_gap',
                'error': f"Gap in cumulative tag chain: @{layer_type} (Layer {layer_num}) missing but higher layers present"
            })

    return errors


def validate_all_cumulative_tags(tags_data: Dict) -> List[Dict]:
    """Validate cumulative tagging for all artifacts.

    Returns:
        List of cumulative tagging errors
    """
    errors = []

    for file_path, data in tags_data.items():
        tags = data.get('tags', {})

        # Skip files without tags
        if not tags or tags == {'impl-status': []}:
            continue

        # Detect artifact layer
        artifact_layer = detect_artifact_layer(file_path, tags)

        if artifact_layer is None:
            # Cannot determine layer, skip cumulative validation
            continue

        # Validate cumulative tags
        cumulative_errors = validate_cumulative_tags(file_path, tags, artifact_layer)
        errors.extend(cumulative_errors)

    return errors


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
    parser.add_argument(
        '--validate-cumulative',
        action='store_true',
        help='Enable cumulative tagging hierarchy validation'
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

    # Validate cumulative tagging (if enabled)
    cumulative_errors = []
    if args.validate_cumulative:
        print("Validating cumulative tagging hierarchy...")
        cumulative_errors = validate_all_cumulative_tags(tags_data)

    # Print results
    print(generate_error_report(errors))

    if cumulative_errors:
        print("")
        print("=" * 80)
        print(f"❌ CUMULATIVE TAGGING ERRORS FOUND: {len(cumulative_errors)}")
        print("=" * 80)
        print("")

        # Group by error type
        errors_by_type = defaultdict(list)
        for error in cumulative_errors:
            errors_by_type[error['error_type']].append(error)

        for error_type, type_errors in sorted(errors_by_type.items()):
            print(f"\n{error_type.upper().replace('_', ' ')}: {len(type_errors)}")
            for error in type_errors[:10]:  # Show first 10 of each type
                print(f"  📄 {error['file']}")
                print(f"     ❌ {error['error']}")
            if len(type_errors) > 10:
                print(f"  ... and {len(type_errors) - 10} more")

        print("")
        print("=" * 80)
    elif args.validate_cumulative:
        print("")
        print("✅ Cumulative tagging validation passed")

    print(generate_coverage_report(tags_data, doc_index))

    # Return exit code
    total_errors = len(errors) + len(cumulative_errors)
    if args.strict and total_errors > 0:
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
