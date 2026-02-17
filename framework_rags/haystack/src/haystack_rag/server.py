#!/usr/bin/env python3
"""Haystack RAG server entry point for Hayhooks."""

import os
import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from haystack_rag.config import load_config
from haystack_rag.pipelines import create_indexing_pipeline, create_query_pipeline


def setup_pipelines(pipelines_dir: Path | None = None) -> dict:
    """Setup and export pipelines for Hayhooks.

    Args:
        pipelines_dir: Directory to export pipeline YAMLs.

    Returns:
        Dictionary of pipeline names to pipelines.
    """
    config = load_config()

    pipelines = {
        "indexing": create_indexing_pipeline(config),
        "query": create_query_pipeline(config),
    }

    if pipelines_dir:
        pipelines_dir = Path(pipelines_dir)
        pipelines_dir.mkdir(parents=True, exist_ok=True)

        for name, pipeline in pipelines.items():
            yaml_path = pipelines_dir / f"{name}.yaml"
            with open(yaml_path, "w") as f:
                f.write(pipeline.dumps())
            print(f"Exported {name} pipeline to {yaml_path}")

    return pipelines


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Haystack RAG Server")
    parser.add_argument("--export-dir", help="Export pipelines to directory")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=1416)
    args = parser.parse_args()

    if args.export_dir:
        setup_pipelines(Path(args.export_dir))
        return

    # Start Hayhooks server
    print(f"Starting Hayhooks server on {args.host}:{args.port}")
    print("Pipelines will be loaded from HAYHOOKS_PIPELINES_DIR")

    # Hayhooks is typically started via CLI, this is for programmatic use
    try:
        from hayhooks import server
        server.run(host=args.host, port=args.port)
    except ImportError:
        print("Hayhooks not installed. Run: pip install hayhooks[mcp]")
        sys.exit(1)


if __name__ == "__main__":
    main()
