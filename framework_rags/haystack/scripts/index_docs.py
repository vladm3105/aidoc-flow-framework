#!/usr/bin/env python3
"""Index documents into Haystack RAG service."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from haystack_rag.config import load_config
from haystack_rag.pipelines import create_indexing_pipeline


def scan_documents(source_dir: Path, extensions: list[str] | None = None) -> list[Path]:
    """Scan directory for markdown documents."""
    if extensions is None:
        extensions = [".md"]

    docs = []
    for ext in extensions:
        docs.extend(source_dir.rglob(f"*{ext}"))

    # Filter out templates and backups
    docs = [
        d for d in docs
        if "TEMPLATE" not in d.name
        and "backup_" not in str(d)
        and not d.name.startswith(".")
    ]

    return sorted(docs)


def main():
    parser = argparse.ArgumentParser(description="Index documents into Haystack")
    parser.add_argument("--source", required=True, help="Source directory")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    if not source_dir.exists():
        print(f"Error: Source not found: {source_dir}")
        return 1

    docs = scan_documents(source_dir)
    print(f"Found {len(docs)} documents")

    if args.dry_run:
        for doc in docs[:10]:
            print(f"  {doc.name}")
        if len(docs) > 10:
            print(f"  ... and {len(docs) - 10} more")
        return 0

    # Create pipeline
    config = load_config()
    pipeline = create_indexing_pipeline(config)

    # Index documents
    indexed = 0
    for doc_path in docs:
        try:
            result = pipeline.run({"converter": {"sources": [str(doc_path)]}})
            indexed += 1
            if args.verbose:
                print(f"  ✓ {doc_path.name}")
        except Exception as e:
            print(f"  ✗ {doc_path.name}: {e}")

    print(f"\nIndexed {indexed}/{len(docs)} documents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
