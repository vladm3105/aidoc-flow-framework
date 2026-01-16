#!/usr/bin/env python3
"""
Forward Reference Validator for SDD Documents

Prevents upstream documents from referencing specific downstream IDs.
Enforces SDD layer hierarchy: upstream docs cannot cite specific IDs
from layers that don't exist yet.

Error Codes:
- FWDREF-E001: Specific downstream ID in upstream doc
- FWDREF-E002: Non-existent downstream reference
- FWDREF-W001: Downstream count claim
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from error_codes import format_error, calculate_exit_code


# SDD Layer Map - defines the creation order of artifacts
LAYER_MAP = {
    "BRD": 1,
    "PRD": 2,
    "EARS": 3,
    "BDD": 4,
    "ADR": 5,
    "SYS": 6,
    "REQ": 7,
    "IMPL": 8,
    "CTR": 9,
    "SPEC": 10,
    "TASKS": 11,
}

# Regex pattern for document IDs
DOC_ID_PATTERN = re.compile(
    r'\b(BRD|PRD|EARS|BDD|ADR|SYS|REQ|IMPL|CTR|SPEC|TASKS)-(\d{2,})\b'
)

# Regex pattern for element IDs (dot notation)
ELEMENT_ID_PATTERN = re.compile(
    r'\b(BRD|PRD|EARS|BDD|ADR|SYS|REQ|IMPL|CTR|SPEC|TASKS)\.(\d{2,})\.(\d{2})\.(\d{2,})\b'
)


def get_document_type(filepath: str) -> Optional[str]:
    """
    Determine document type from filename.

    Args:
        filepath: Path to document

    Returns:
        Document type (e.g., 'PRD', 'ADR') or None
    """
    filename = os.path.basename(filepath)

    # Match patterns like PRD-001.md, ADR-001_title.md, PRD-001.5_section.md
    match = re.match(r'^([A-Z]+)-\d+', filename)
    if match:
        doc_type = match.group(1)
        if doc_type in LAYER_MAP:
            return doc_type

    # Check directory name as fallback
    dirname = os.path.basename(os.path.dirname(filepath))
    if dirname.upper() in LAYER_MAP:
        return dirname.upper()

    return None


def get_document_layer(doc_type: str) -> int:
    """Get the layer number for a document type."""
    return LAYER_MAP.get(doc_type, 0)


def extract_document_references(content: str) -> List[Tuple[str, str, int]]:
    """
    Extract all document ID references from content.

    Returns list of (doc_type, doc_id, line_number)
    """
    references = []

    for match in DOC_ID_PATTERN.finditer(content):
        doc_type = match.group(1)
        doc_id = match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        references.append((doc_type, doc_id, line_num))

    # Also check element IDs
    for match in ELEMENT_ID_PATTERN.finditer(content):
        doc_type = match.group(1)
        doc_id = match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        references.append((doc_type, doc_id, line_num))

    return references


def find_document_count_claims(content: str) -> List[Tuple[str, int, int]]:
    """
    Find claims about counts of downstream documents.

    Returns list of (doc_type, count, line_number)
    """
    claims = []

    # Pattern: "5 ADRs", "3 REQ documents", "ADR-01 through ADR-05"
    patterns = [
        r'(\d+)\s+(ADR|SYS|REQ|SPEC|TASKS|IMPL|CTR)s?\b',
        r'(ADR|SYS|REQ|SPEC|TASKS|IMPL|CTR)-\d+\s+through\s+\1-(\d+)',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            if match.lastindex >= 2:
                if match.group(1).isdigit():
                    count = int(match.group(1))
                    doc_type = match.group(2).upper()
                else:
                    count = int(match.group(2))
                    doc_type = match.group(1).upper()

                line_num = content[:match.start()].count('\n') + 1
                claims.append((doc_type, count, line_num))

    return claims


def check_document_exists(doc_type: str, doc_id: str, search_dirs: List[str]) -> bool:
    """
    Check if a referenced document exists.

    Args:
        doc_type: Document type (e.g., 'ADR')
        doc_id: Document number (e.g., '001')
        search_dirs: Directories to search

    Returns:
        True if document exists
    """
    patterns = [
        f"{doc_type}-{doc_id}*.md",
        f"{doc_type}-{doc_id.lstrip('0')}*.md",  # Try without leading zeros
        f"{doc_type.lower()}-{doc_id}*.md",
    ]

    for search_dir in search_dirs:
        for pattern in patterns:
            matches = glob.glob(os.path.join(search_dir, '**', pattern), recursive=True)
            if matches:
                return True

    return False


def validate_forward_references(
    filepath: str,
    search_dirs: Optional[List[str]] = None
) -> Tuple[List[str], List[str]]:
    """
    Validate forward references in a document.

    Args:
        filepath: Path to document to validate
        search_dirs: Directories to search for referenced documents

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    # Determine source document type and layer
    source_type = get_document_type(filepath)
    if not source_type:
        # Not an SDD document, skip
        return errors, warnings

    source_layer = get_document_layer(source_type)
    filename = os.path.basename(filepath)

    # Set up search directories
    if search_dirs is None:
        search_dirs = [os.path.dirname(filepath), '.']

    # Read document content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract references
    references = extract_document_references(content)

    for ref_type, ref_id, line_num in references:
        ref_layer = get_document_layer(ref_type)

        # Check for forward reference (referencing downstream layer)
        if ref_layer > source_layer:
            # Check if the referenced document exists
            exists = check_document_exists(ref_type, ref_id, search_dirs)

            if not exists:
                errors.append(format_error(
                    "FWDREF-E001",
                    f"{filename}:{line_num}: {source_type} (Layer {source_layer}) "
                    f"references {ref_type}-{ref_id} (Layer {ref_layer}) which doesn't exist yet"
                ))
            else:
                # Document exists, but let's warn if it's a significantly downstream layer
                if ref_layer - source_layer > 2:
                    warnings.append(format_error(
                        "FWDREF-W001",
                        f"{filename}:{line_num}: {source_type} references far downstream "
                        f"{ref_type}-{ref_id}"
                    ))

    # Check for count claims about downstream documents
    count_claims = find_document_count_claims(content)

    for doc_type, count, line_num in count_claims:
        ref_layer = get_document_layer(doc_type)

        if ref_layer > source_layer:
            warnings.append(format_error(
                "FWDREF-W001",
                f"{filename}:{line_num}: Claims {count} {doc_type}s but {doc_type} "
                f"is Layer {ref_layer}, created after {source_type} (Layer {source_layer})"
            ))

    return errors, warnings


def find_sdd_documents(directory: str) -> List[str]:
    """Find all SDD documents in a directory tree."""
    documents = []

    for doc_type in LAYER_MAP.keys():
        # Search for both uppercase and lowercase patterns
        patterns = [
            os.path.join(directory, '**', f'{doc_type}-*.md'),
            os.path.join(directory, '**', f'{doc_type.lower()}-*.md'),
        ]

        for pattern in patterns:
            documents.extend(glob.glob(pattern, recursive=True))

    return list(set(documents))  # Deduplicate


def main():
    parser = argparse.ArgumentParser(
        description="Validate forward references in SDD documents"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to document or directory to scan"
    )
    parser.add_argument(
        "--search-dir",
        action="append",
        dest="search_dirs",
        help="Additional directories to search for referenced documents"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    args = parser.parse_args()

    all_errors = []
    all_warnings = []

    search_dirs = args.search_dirs or []

    if os.path.isfile(args.path):
        search_dirs.insert(0, os.path.dirname(args.path))
        errors, warnings = validate_forward_references(args.path, search_dirs)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    else:
        search_dirs.insert(0, args.path)
        documents = find_sdd_documents(args.path)

        for filepath in documents:
            errors, warnings = validate_forward_references(filepath, search_dirs)
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
        print("Forward reference validation passed")

    sys.exit(calculate_exit_code(all_errors, all_warnings, args.strict))


if __name__ == "__main__":
    main()
