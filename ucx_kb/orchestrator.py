"""Ingestion orchestrator for ucx_kb."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ucx_kb.graph.adapter import kb_extract
from ucx_kb.rag.adapter import kb_embed
from ucx_kb.utils import is_real_document


def ingest_file(file_path: str, extractor: str | None = None, commit_graph: bool = True) -> dict:
    rag_result = kb_embed(file_path=file_path, force=False)
    graph_result = kb_extract(file_path=file_path, extractor=extractor, commit=commit_graph)
    return {
        "file_path": file_path,
        "rag": rag_result.to_dict(),
        "graph": graph_result.to_dict(),
    }


def ingest_folder(folder: str, pattern: str = "*.yaml", extractor: str | None = None) -> dict:
    root = Path(folder)
    files = [p for p in root.rglob(pattern) if p.is_file() and is_real_document(str(p))]
    results = []
    errors = 0

    for file_path in files:
        try:
            results.append(ingest_file(str(file_path), extractor=extractor))
        except Exception as e:
            errors += 1
            results.append({"file_path": str(file_path), "error": str(e)})

    return {
        "root": str(root),
        "total_files": len(files),
        "errors": errors,
        "results": results,
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run ucx_kb ingestion pipeline")
    parser.add_argument("path", help="File or folder path")
    parser.add_argument("--pattern", default="*.yaml")
    parser.add_argument("--extractor", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    path = Path(args.path)
    if path.is_file():
        payload = ingest_file(str(path), extractor=args.extractor)
    else:
        payload = ingest_folder(str(path), pattern=args.pattern, extractor=args.extractor)

    text = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
