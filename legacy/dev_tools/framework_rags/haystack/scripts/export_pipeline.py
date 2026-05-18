#!/usr/bin/env python3
"""Export Haystack pipelines to YAML for Hayhooks."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from haystack_rag.config import load_config
from haystack_rag.pipelines import create_indexing_pipeline, create_query_pipeline


def main():
    """Export pipelines to YAML files."""
    pipelines_dir = Path(__file__).parent.parent / "pipelines"
    pipelines_dir.mkdir(exist_ok=True)

    config = load_config()

    print("Exporting pipelines...")

    # Export indexing pipeline
    try:
        indexing_pipeline = create_indexing_pipeline(config)
        indexing_yaml = pipelines_dir / "indexing.yaml"
        with open(indexing_yaml, "w") as f:
            f.write(indexing_pipeline.dumps())
        print(f"  ✓ Indexing pipeline: {indexing_yaml}")
    except Exception as e:
        print(f"  ✗ Indexing pipeline: {e}")

    # Export query pipeline
    try:
        query_pipeline = create_query_pipeline(config)
        query_yaml = pipelines_dir / "query.yaml"
        with open(query_yaml, "w") as f:
            f.write(query_pipeline.dumps())
        print(f"  ✓ Query pipeline: {query_yaml}")
    except Exception as e:
        print(f"  ✗ Query pipeline: {e}")

    print("\nPipelines exported to:", pipelines_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
