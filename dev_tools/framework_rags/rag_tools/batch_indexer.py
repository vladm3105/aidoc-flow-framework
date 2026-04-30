#!/usr/bin/env python3
"""Batch indexer for both Haystack and LightRAG services."""

import argparse
import time
from pathlib import Path

import httpx


# Batch limits
LIGHTRAG_BATCH_SIZE = 40  # 30-50 recommended, using 40
HAYSTACK_BATCH_SIZE = 100  # No strict limit for embeddings


def scan_documents(source_dir: Path, extensions: list[str] | None = None) -> list[Path]:
    """Scan directory for documents to index.

    Args:
        source_dir: Directory to scan.
        extensions: File extensions to include. Defaults to [".md"].

    Returns:
        List of document paths.
    """
    if extensions is None:
        extensions = [".md"]

    docs = []
    for ext in extensions:
        docs.extend(source_dir.rglob(f"*{ext}"))

    # Filter out templates and examples
    docs = [
        d for d in docs
        if "TEMPLATE" not in d.name
        and "example" not in d.name.lower()
        and "backup_" not in str(d)
    ]

    return sorted(docs)


def index_haystack(docs: list[Path], base_url: str = "http://localhost:1416", verbose: bool = False) -> int:
    """Index documents into Haystack.

    Args:
        docs: List of document paths.
        base_url: Haystack API URL.
        verbose: Print progress.

    Returns:
        Number of documents indexed.
    """
    indexed = 0

    print(f"\nIndexing {len(docs)} documents into Haystack...")

    for i in range(0, len(docs), HAYSTACK_BATCH_SIZE):
        batch = docs[i:i + HAYSTACK_BATCH_SIZE]

        for doc_path in batch:
            try:
                content = doc_path.read_text(encoding="utf-8")

                response = httpx.post(
                    f"{base_url}/index",
                    json={
                        "content": content,
                        "meta": {
                            "file_path": str(doc_path),
                            "filename": doc_path.name,
                        }
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    indexed += 1
                    if verbose:
                        print(f"  ✓ {doc_path.name}")
                else:
                    print(f"  ✗ {doc_path.name}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  ✗ {doc_path.name}: {e}")

        print(f"  Batch {i // HAYSTACK_BATCH_SIZE + 1}: {len(batch)} docs processed")

    return indexed


def index_lightrag(docs: list[Path], base_url: str = "http://localhost:9621",
                   api_key: str = "lightragsecretkey", verbose: bool = False) -> int:
    """Index documents into LightRAG.

    Args:
        docs: List of document paths.
        base_url: LightRAG API URL.
        api_key: API authentication key.
        verbose: Print progress.

    Returns:
        Number of documents indexed.
    """
    indexed = 0
    headers = {"X-API-Key": api_key}

    print(f"\nIndexing {len(docs)} documents into LightRAG...")
    print(f"  Using batch size: {LIGHTRAG_BATCH_SIZE} (to prevent server hang)")

    for i in range(0, len(docs), LIGHTRAG_BATCH_SIZE):
        batch = docs[i:i + LIGHTRAG_BATCH_SIZE]
        batch_num = i // LIGHTRAG_BATCH_SIZE + 1
        total_batches = (len(docs) + LIGHTRAG_BATCH_SIZE - 1) // LIGHTRAG_BATCH_SIZE

        print(f"\n  Batch {batch_num}/{total_batches}:")

        for doc_path in batch:
            try:
                content = doc_path.read_text(encoding="utf-8")

                response = httpx.post(
                    f"{base_url}/documents/text",
                    headers=headers,
                    json={"text": content, "metadata": {"source": str(doc_path)}},
                    timeout=180,  # LLM extraction can be slow
                )

                if response.status_code == 200:
                    indexed += 1
                    if verbose:
                        print(f"    ✓ {doc_path.name}")
                else:
                    print(f"    ✗ {doc_path.name}: HTTP {response.status_code}")

            except httpx.TimeoutException:
                print(f"    ⚠ {doc_path.name}: Timeout (may still be processing)")
            except Exception as e:
                print(f"    ✗ {doc_path.name}: {e}")

        # Check health between batches
        try:
            health = httpx.get(f"{base_url}/health", headers=headers, timeout=10)
            if health.status_code != 200:
                print("  ⚠ LightRAG health check failed, waiting 30s...")
                time.sleep(30)
        except Exception:
            print("  ⚠ LightRAG not responding, waiting 60s...")
            time.sleep(60)

        print(f"  Batch {batch_num} complete: {len(batch)} docs processed")

    return indexed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Index documents into RAG services")
    parser.add_argument("--source", required=True, help="Source directory to scan")
    parser.add_argument("--service", choices=["haystack", "lightrag", "both"],
                       default="both", help="Which service to index")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, don't index")
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return 1

    docs = scan_documents(source_dir)
    print(f"\nFound {len(docs)} documents in {source_dir}")

    if args.dry_run:
        print("\nDry run - documents to index:")
        for doc in docs[:20]:
            print(f"  {doc.relative_to(source_dir)}")
        if len(docs) > 20:
            print(f"  ... and {len(docs) - 20} more")
        return 0

    total_indexed = 0

    if args.service in ("haystack", "both"):
        count = index_haystack(docs, verbose=args.verbose)
        print(f"\nHaystack: Indexed {count}/{len(docs)} documents")
        total_indexed += count

    if args.service in ("lightrag", "both"):
        count = index_lightrag(docs, verbose=args.verbose)
        print(f"\nLightRAG: Indexed {count}/{len(docs)} documents")
        total_indexed += count

    print(f"\nTotal indexed: {total_indexed}")
    return 0


if __name__ == "__main__":
    exit(main())
