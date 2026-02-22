#!/usr/bin/env python3
"""Batch indexer for project_knowledge contract jobs.

Generates JSONL job artifacts for downstream RAG embed and Graph extract workers.
"""

import argparse
import json
from pathlib import Path

RAG_BATCH_SIZE = 100
GRAPH_BATCH_SIZE = 40


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


def _write_jobs(path: Path, jobs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for job in jobs:
            f.write(json.dumps(job, ensure_ascii=False) + "\n")


def build_rag_jobs(docs: list[Path]) -> list[dict]:
    jobs: list[dict] = []
    for doc_path in docs:
        jobs.append(
            {
                "route": "kb_embed",
                "request": {
                    "contract_version": "v1",
                    "file_path": str(doc_path),
                    "force": False,
                },
            }
        )
    return jobs


def build_graph_jobs(docs: list[Path]) -> list[dict]:
    jobs: list[dict] = []
    for doc_path in docs:
        jobs.append(
            {
                "route": "kb_extract",
                "request": {
                    "contract_version": "v1",
                    "file_path": str(doc_path),
                    "commit": True,
                },
            }
        )
    return jobs


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate project_knowledge indexing jobs")
    parser.add_argument("--source", required=True, help="Source directory to scan")
    parser.add_argument("--service", choices=["rag", "graph", "both"],
                       default="both", help="Which project_knowledge pipeline to target")
    parser.add_argument("--out", default="project_knowledge/tmp/jobs", help="Output directory for job files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, do not write jobs")
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

    output_dir = Path(args.out).resolve()
    total_jobs = 0

    if args.service in ("rag", "both"):
        rag_jobs = build_rag_jobs(docs)
        rag_path = output_dir / "rag_embed_jobs.jsonl"
        _write_jobs(rag_path, rag_jobs)
        total_jobs += len(rag_jobs)
        print(f"\nRAG jobs written: {rag_path} ({len(rag_jobs)} jobs, batch_size={RAG_BATCH_SIZE})")

    if args.service in ("graph", "both"):
        graph_jobs = build_graph_jobs(docs)
        graph_path = output_dir / "graph_extract_jobs.jsonl"
        _write_jobs(graph_path, graph_jobs)
        total_jobs += len(graph_jobs)
        print(f"\nGraph jobs written: {graph_path} ({len(graph_jobs)} jobs, batch_size={GRAPH_BATCH_SIZE})")

    print(f"\nTotal jobs generated: {total_jobs}")
    return 0


if __name__ == "__main__":
    exit(main())
