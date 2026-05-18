#!/usr/bin/env python3
"""Document scanner for framework documentation."""

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocumentInfo:
    """Information about a scanned document."""
    path: Path
    doc_type: str | None
    layer: int | None
    size_bytes: int
    has_frontmatter: bool


# SDD layer mapping (Layer 0 = Reference documents)
LAYER_MAPPING = {
    "REF": 0,  # Initial project documentation, business requirements
    "BRD": 1, "PRD": 2, "EARS": 3, "BDD": 4, "ADR": 5,
    "SYS": 6, "REQ": 7, "CTR": 8, "SPEC": 9, "TSPEC": 10,
    "TASKS": 11, "IPLAN": 12,
}


def scan_directory(
    source_dir: Path,
    extensions: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
) -> list[DocumentInfo]:
    """Scan directory for documents.

    Args:
        source_dir: Directory to scan.
        extensions: File extensions to include.
        exclude_patterns: Patterns to exclude from results.

    Returns:
        List of DocumentInfo objects.
    """
    if extensions is None:
        extensions = [".md"]

    if exclude_patterns is None:
        exclude_patterns = ["TEMPLATE", "backup_", "example", ".git"]

    docs = []

    for ext in extensions:
        for file_path in source_dir.rglob(f"*{ext}"):
            # Check exclusions
            path_str = str(file_path)
            if any(pattern in path_str for pattern in exclude_patterns):
                continue

            # Get document info
            doc_info = analyze_document(file_path)
            docs.append(doc_info)

    return sorted(docs, key=lambda d: (d.layer or 99, d.path))


def analyze_document(file_path: Path) -> DocumentInfo:
    """Analyze a single document.

    Args:
        file_path: Path to document.

    Returns:
        DocumentInfo object.
    """
    content = file_path.read_text(encoding="utf-8", errors="ignore")

    # Check for frontmatter
    has_frontmatter = content.startswith("---")

    # Detect doc_type from filename or path
    doc_type = None
    layer = None

    # Try filename first (e.g., PRD-001.md)
    filename = file_path.stem.upper()
    for dtype in LAYER_MAPPING:
        if filename.startswith(dtype):
            doc_type = dtype
            layer = LAYER_MAPPING[dtype]
            break

    # Try directory name (e.g., 02_PRD/)
    if doc_type is None:
        for part in file_path.parts:
            for dtype in LAYER_MAPPING:
                if dtype in part.upper():
                    doc_type = dtype
                    layer = LAYER_MAPPING[dtype]
                    break
            if doc_type:
                break

    return DocumentInfo(
        path=file_path,
        doc_type=doc_type,
        layer=layer,
        size_bytes=file_path.stat().st_size,
        has_frontmatter=has_frontmatter,
    )


def print_summary(docs: list[DocumentInfo], verbose: bool = False):
    """Print scan summary.

    Args:
        docs: List of documents.
        verbose: Show detailed listing.
    """
    print(f"\nScanned {len(docs)} documents\n")

    # Group by layer
    by_layer: dict[int | None, list[DocumentInfo]] = {}
    for doc in docs:
        layer = doc.layer
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(doc)

    # Print summary by layer
    print("Documents by Layer:")
    print("-" * 40)

    for layer in sorted(k for k in by_layer.keys() if k is not None):
        layer_docs = by_layer[layer]
        doc_type = layer_docs[0].doc_type if layer_docs else "Unknown"
        print(f"  L{layer:02d} ({doc_type}): {len(layer_docs)} documents")

        if verbose:
            for doc in layer_docs[:5]:
                print(f"       - {doc.path.name}")
            if len(layer_docs) > 5:
                print(f"       ... and {len(layer_docs) - 5} more")

    # Uncategorized
    if None in by_layer:
        uncategorized = by_layer[None]
        print(f"\n  Uncategorized: {len(uncategorized)} documents")
        if verbose:
            for doc in uncategorized[:5]:
                print(f"       - {doc.path.name}")

    # Statistics
    total_size = sum(d.size_bytes for d in docs)
    with_frontmatter = sum(1 for d in docs if d.has_frontmatter)

    print(f"\nStatistics:")
    print(f"  Total size: {total_size / 1024:.1f} KB")
    print(f"  With frontmatter: {with_frontmatter}/{len(docs)} ({100*with_frontmatter/len(docs):.0f}%)")


def main():
    parser = argparse.ArgumentParser(description="Scan framework documentation")
    parser.add_argument("--source", required=True, help="Source directory")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--layer", type=int, help="Filter by layer")
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    if not source_dir.exists():
        print(f"Error: Source not found: {source_dir}")
        return 1

    docs = scan_directory(source_dir)

    # Filter by layer if specified
    if args.layer:
        docs = [d for d in docs if d.layer == args.layer]

    if args.json:
        import json
        output = [
            {
                "path": str(d.path),
                "doc_type": d.doc_type,
                "layer": d.layer,
                "size_bytes": d.size_bytes,
                "has_frontmatter": d.has_frontmatter,
            }
            for d in docs
        ]
        print(json.dumps(output, indent=2))
    else:
        print_summary(docs, verbose=args.verbose)

    return 0


if __name__ == "__main__":
    exit(main())
