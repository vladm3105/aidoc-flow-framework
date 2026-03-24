"""Forward reference validation for SDD documents.

Prevents upstream documents from referencing specific downstream IDs
that don't exist yet, enforcing SDD layer hierarchy.

Error Codes:
- FWDREF-E001: Forward reference to non-existent downstream document
- FWDREF-W001: Forward reference to far downstream layer
- FWDREF-W002: Count claim about downstream documents
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ucx.validators.common.result import (
    UnifiedValidationResult,
    ValidationTier,
)

# SDD Layer Map - defines the creation order of artifacts
LAYER_MAP: Dict[str, int] = {
    "BRD": 1,
    "PRD": 2,
    "EARS": 3,
    "BDD": 4,
    "ADR": 5,
    "SYS": 6,
    "REQ": 7,
    "CTR": 8,
    "SPEC": 9,
    "TSPEC": 10,
    "TASKS": 11,
}

# Regex patterns
DOC_ID_PATTERN = re.compile(
    r'\b(BRD|PRD|EARS|BDD|ADR|SYS|REQ|CTR|SPEC|TSPEC|TASKS)-(\d{2,})\b'
)

ELEMENT_ID_PATTERN = re.compile(
    r'\b(BRD|PRD|EARS|BDD|ADR|SYS|REQ|CTR|SPEC|TSPEC|TASKS)\.(\d{2,})\.(\d{2})\.(\d{2,})\b'
)


def get_document_type_from_path(file_path: Path) -> Optional[str]:
    """
    Determine document type from file path.

    Args:
        file_path: Path to document

    Returns:
        Document type (e.g., 'BRD', 'PRD') or None
    """
    filename = file_path.name

    # Match patterns like BRD-01.md, PRD-001_title.md, BRD-01.5_section.md
    match = re.match(r'^([A-Z]+)-\d+', filename)
    if match:
        doc_type = match.group(1)
        if doc_type in LAYER_MAP:
            return doc_type

    # Check directory name as fallback
    parent_name = file_path.parent.name.upper()
    for layer_type in LAYER_MAP:
        if layer_type in parent_name:
            return layer_type

    return None


def get_document_layer(doc_type: str) -> int:
    """Get the layer number for a document type."""
    return LAYER_MAP.get(doc_type, 0)


def extract_document_references(
    content: str
) -> List[Tuple[str, str, int]]:
    """
    Extract all document ID references from content.

    Returns:
        List of (doc_type, doc_id, line_number)
    """
    references = []
    lines = content.splitlines()

    for line_no, line in enumerate(lines, start=1):
        # Check document IDs
        for match in DOC_ID_PATTERN.finditer(line):
            doc_type = match.group(1)
            doc_id = match.group(2)
            references.append((doc_type, doc_id, line_no))

        # Check element IDs
        for match in ELEMENT_ID_PATTERN.finditer(line):
            doc_type = match.group(1)
            doc_id = match.group(2)
            references.append((doc_type, doc_id, line_no))

    return references


def find_count_claims(content: str) -> List[Tuple[str, int, int]]:
    """
    Find claims about counts of downstream documents.

    Returns:
        List of (doc_type, count, line_number)
    """
    claims = []
    lines = content.splitlines()

    # Pattern: "5 ADRs", "3 REQ documents"
    count_pattern = re.compile(
        r'(\d+)\s+(ADR|SYS|REQ|SPEC|TASKS|CTR|TSPEC)s?\b',
        re.IGNORECASE
    )

    for line_no, line in enumerate(lines, start=1):
        for match in count_pattern.finditer(line):
            count = int(match.group(1))
            doc_type = match.group(2).upper()
            claims.append((doc_type, count, line_no))

    return claims


def check_document_exists(
    doc_type: str,
    doc_id: str,
    search_paths: List[Path],
) -> bool:
    """
    Check if a referenced document exists.

    Args:
        doc_type: Document type (e.g., 'ADR')
        doc_id: Document number (e.g., '001')
        search_paths: Directories to search

    Returns:
        True if document exists
    """
    patterns = [
        f"{doc_type}-{doc_id}*.md",
        f"{doc_type}-{doc_id.lstrip('0')}*.md",  # Without leading zeros
        f"{doc_type.lower()}-{doc_id}*.md",
    ]

    for search_path in search_paths:
        if not search_path.is_dir():
            continue

        for pattern in patterns:
            matches = list(search_path.rglob(pattern))
            if matches:
                return True

    return False


def validate_forward_references(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
    search_paths: Optional[List[Path]] = None,
) -> None:
    """
    Validate forward references in a document.

    Args:
        content: File content
        file_path: Path to file
        result: Result to populate
        search_paths: Directories to search for referenced documents
    """
    # Determine source document type and layer
    source_type = get_document_type_from_path(file_path)
    if not source_type:
        return  # Not an SDD document

    source_layer = get_document_layer(source_type)

    # Set up search paths
    if search_paths is None:
        search_paths = [file_path.parent, file_path.parent.parent]

    # Extract references
    references = extract_document_references(content)

    for ref_type, ref_id, line_no in references:
        ref_layer = get_document_layer(ref_type)

        # Check for forward reference (referencing downstream layer)
        if ref_layer > source_layer:
            exists = check_document_exists(ref_type, ref_id, search_paths)

            if not exists:
                result.add_issue(
                    "FWDREF-E001",
                    file_path=file_path,
                    line=line_no,
                    context=(
                        f"{source_type} (L{source_layer}) references "
                        f"{ref_type}-{ref_id} (L{ref_layer}) which doesn't exist"
                    ),
                    tier=ValidationTier.TIER2,
                )
            elif ref_layer - source_layer > 2:
                # Warn about far downstream references
                result.add_issue(
                    "FWDREF-W001",
                    file_path=file_path,
                    line=line_no,
                    context=(
                        f"{source_type} references far downstream "
                        f"{ref_type}-{ref_id} ({ref_layer - source_layer} layers ahead)"
                    ),
                    tier=ValidationTier.TIER2,
                )

    # Check count claims about downstream documents
    count_claims = find_count_claims(content)

    for doc_type, count, line_no in count_claims:
        ref_layer = get_document_layer(doc_type)

        if ref_layer > source_layer:
            result.add_issue(
                "FWDREF-W002",
                file_path=file_path,
                line=line_no,
                context=(
                    f"Claims {count} {doc_type}s but {doc_type} "
                    f"(L{ref_layer}) is created after {source_type} (L{source_layer})"
                ),
                tier=ValidationTier.TIER2,
            )


__all__ = [
    "validate_forward_references",
    "get_document_type_from_path",
    "get_document_layer",
    "LAYER_MAP",
]
