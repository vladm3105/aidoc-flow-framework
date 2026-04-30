#!/usr/bin/env python3
"""Backfill legacy documents into ucx_knowledge using orchestrator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ucx_knowledge.orchestrator import ingest_folder


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill legacy document corpus")
    parser.add_argument("--source", required=True, help="Legacy source folder")
    parser.add_argument("--pattern", default="*.yaml", help="Glob pattern")
    parser.add_argument("--extractor", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", default="ucx_knowledge/tmp/backfill_report.json")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    if not source.exists():
        raise SystemExit(f"Source not found: {source}")

    if args.dry_run:
        files = [str(p) for p in source.rglob(args.pattern) if p.is_file()]
        payload = {"source": str(source), "dry_run": True, "files": files, "count": len(files)}
    else:
        payload = ingest_folder(str(source), pattern=args.pattern, extractor=args.extractor)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
