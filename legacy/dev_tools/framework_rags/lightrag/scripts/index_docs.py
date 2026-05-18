#!/usr/bin/env python3
"""Index documents into LightRAG service with batch processing."""

import argparse
import sys
import time
from pathlib import Path

import httpx

# Batch limit to prevent server hang
BATCH_SIZE = 40  # 30-50 recommended


def scan_documents(source_dir: Path) -> list[Path]:
    """Scan directory for markdown documents."""
    docs = list(source_dir.rglob("*.md"))

    # Filter out templates and backups
    docs = [
        d for d in docs
        if "TEMPLATE" not in d.name
        and "backup_" not in str(d)
        and not d.name.startswith(".")
    ]

    return sorted(docs)


def check_health(base_url: str, api_key: str) -> bool:
    """Check LightRAG server health."""
    try:
        response = httpx.get(
            f"{base_url}/health",
            headers={"X-API-Key": api_key},
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def index_document(base_url: str, api_key: str, doc_path: Path) -> bool:
    """Index a single document."""
    try:
        content = doc_path.read_text(encoding="utf-8")

        response = httpx.post(
            f"{base_url}/documents/text",
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            json={
                "text": content,
                "metadata": {
                    "source": str(doc_path),
                    "filename": doc_path.name,
                }
            },
            timeout=180,  # LLM extraction can be slow
        )

        return response.status_code == 200
    except httpx.TimeoutException:
        return None  # Timeout, may still be processing
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Index documents into LightRAG")
    parser.add_argument("--source", required=True, help="Source directory")
    parser.add_argument("--base-url", default="http://localhost:9621")
    parser.add_argument("--api-key", default="lightragsecretkey")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    if not source_dir.exists():
        print(f"Error: Source not found: {source_dir}")
        return 1

    docs = scan_documents(source_dir)
    print(f"Found {len(docs)} documents")
    print(f"Using batch size: {args.batch_size}")

    if args.dry_run:
        for doc in docs[:10]:
            print(f"  {doc.name}")
        if len(docs) > 10:
            print(f"  ... and {len(docs) - 10} more")
        return 0

    # Check server health
    if not check_health(args.base_url, args.api_key):
        print("Error: LightRAG server not healthy")
        return 1

    # Process in batches
    indexed = 0
    failed = 0
    timeouts = 0

    total_batches = (len(docs) + args.batch_size - 1) // args.batch_size

    for batch_num, i in enumerate(range(0, len(docs), args.batch_size), 1):
        batch = docs[i:i + args.batch_size]
        print(f"\nBatch {batch_num}/{total_batches}:")

        for doc_path in batch:
            result = index_document(args.base_url, args.api_key, doc_path)

            if result is True:
                indexed += 1
                if args.verbose:
                    print(f"  ✓ {doc_path.name}")
            elif result is None:
                timeouts += 1
                print(f"  ⚠ {doc_path.name} (timeout)")
            else:
                failed += 1
                print(f"  ✗ {doc_path.name}")

        # Health check between batches
        if not check_health(args.base_url, args.api_key):
            print("\n⚠ Server not responding, waiting 60s...")
            time.sleep(60)
            if not check_health(args.base_url, args.api_key):
                print("Server still not responding, stopping.")
                break

        print(f"  Batch complete: {len(batch)} processed")

    print(f"\nResults:")
    print(f"  Indexed: {indexed}")
    print(f"  Failed: {failed}")
    print(f"  Timeouts: {timeouts}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
