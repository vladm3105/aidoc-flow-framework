#!/usr/bin/env python3
"""Verify LightRAG service health and connectivity."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightrag_service.health import check_all, get_graph_statistics


def main():
    print("LightRAG Service Health Check")
    print("=" * 50)

    statuses = check_all()
    all_healthy = True

    for status in statuses:
        icon = "✓" if status.healthy else "✗"
        color = "\033[32m" if status.healthy else "\033[31m"
        reset = "\033[0m"

        print(f"\n{color}{icon}{reset} {status.service}")
        print(f"  Status: {status.message}")

        if status.details:
            for key, value in status.details.items():
                print(f"  {key}: {value}")

        if not status.healthy:
            all_healthy = False

    # Graph statistics
    print("\n" + "=" * 50)
    print("Knowledge Graph Statistics:")
    stats = get_graph_statistics()

    if "error" in stats:
        print(f"  Error: {stats['error']}")
    else:
        print(f"  Nodes: {stats.get('nodes', 0)}")
        print(f"  Relationships: {stats.get('relationships', 0)}")
        if stats.get("node_types"):
            print("  Node types:")
            for node_type, count in stats["node_types"].items():
                print(f"    - {node_type}: {count}")

    print("\n" + "=" * 50)
    if all_healthy:
        print("\033[32m✓ All checks passed\033[0m")
        return 0
    else:
        print("\033[31m✗ Some checks failed\033[0m")
        return 1


if __name__ == "__main__":
    sys.exit(main())
