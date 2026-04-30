#!/usr/bin/env python3
"""Pilot validation runner for ucx_knowledge rollout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ucx_knowledge.graph.adapter import kb_graph_status
from ucx_knowledge.rag.adapter import kb_status


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ucx_knowledge pilot status")
    parser.add_argument("--out", default="ucx_knowledge/tmp/pilot_validation.json")
    args = parser.parse_args()

    report = {
        "rag_status": kb_status().to_dict(),
        "graph_status": kb_graph_status(),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote validation report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
