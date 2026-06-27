#!/usr/bin/env python3
"""trace_walk — one-shot transitive @-tag walker.

Under the necessary-upstream contract (NECESSARY-UPSTREAM-001), each SDD
layer declares only its direct upstream dependencies in `required_tags`.
Lineage to layers further upstream is reachable transitively through the
@-tag chain (one hop per layer). This tool emits that closure in one
call so the "find every artifact tracing back to BRD-NN" workflow stays
a single command.

Usage:
    trace_walk.py <ARTIFACT-ID> [--to <LAYER>] [--docs <ROOT>]

Output format (one ancestor per line):
    <ARTIFACT-ID> --[hop-N]--> <ANCESTOR-ID>

Sorted by hop count, then by ancestor ID alphabetically.

Exit codes:
    0 — every @-tag encountered resolves on disk
    1 — at least one @-tag in the walked closure is unresolvable
    2 — usage / I/O error
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path

# Shared trace primitives (CFB-PR-2 DD-1) — the single source for the layer
# order, @-tag regex, ID forms, and token→doc-id / doc-id→path helpers, so the
# backward walker (here) and the forward coverage engine agree exactly.
from sdd_trace_graph import (  # sibling module; tools/ is sys.path[0] for a script run
    DOC_FORM,
    LAYER_INDEX,
)
from sdd_trace_graph import (
    doc_id_from_token as _doc_id_from_token,
)
from sdd_trace_graph import (
    emit_tags as _emit_tags,
)
from sdd_trace_graph import (
    locate_doc as _locate_doc,
)


def walk(start_doc_id: str, docs_root: Path) -> tuple[dict[str, int], list[str]]:
    """BFS over the @-tag DAG from ``start_doc_id``.

    Returns ``(hops, unresolved)`` where ``hops[ancestor_doc_id] = N`` and
    ``unresolved`` lists tags that did not resolve on disk.
    """
    hops: dict[str, int] = {start_doc_id: 0}
    unresolved: list[str] = []
    queue: deque[str] = deque([start_doc_id])
    while queue:
        cur = queue.popleft()
        path = _locate_doc(cur, docs_root)
        if path is None:
            if cur != start_doc_id:
                unresolved.append(cur)
            continue
        text = path.read_text(encoding="utf-8")
        for tok in _emit_tags(text):
            target = _doc_id_from_token(tok)
            if target is None:
                unresolved.append(tok)
                continue
            if target == cur:
                continue  # self-tag
            target_path = _locate_doc(target, docs_root)
            if target_path is None:
                unresolved.append(target)
                continue
            if target not in hops:
                hops[target] = hops[cur] + 1
                queue.append(target)
    return hops, unresolved


def _format(start: str, hops: dict[str, int], to_layer: str | None) -> list[str]:
    threshold = LAYER_INDEX.get(to_layer.upper()) if to_layer else 0
    out: list[tuple[int, str, str]] = []
    for ancestor, n in hops.items():
        if ancestor == start:
            continue
        layer = ancestor.split("-", 1)[0]
        if to_layer and LAYER_INDEX.get(layer, 0) < threshold:
            continue
        out.append((n, ancestor, f"{start} --[hop-{n}]--> {ancestor}"))
    out.sort(key=lambda row: (row[0], row[1]))
    return [row[2] for row in out]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="trace_walk", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("artifact_id", help="starting artifact id (e.g. TDD-01)")
    parser.add_argument("--to", help="filter output to ancestors at or above this layer")
    parser.add_argument(
        "--docs",
        type=Path,
        default=Path("docs"),
        help="docs/ root (default: ./docs)",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    if not DOC_FORM.match(args.artifact_id):
        print(f"trace_walk: malformed artifact id '{args.artifact_id}'", file=sys.stderr)
        return 2
    if not args.docs.is_dir():
        print(f"trace_walk: docs root '{args.docs}' is not a directory", file=sys.stderr)
        return 2

    hops, unresolved = walk(args.artifact_id, args.docs)
    for line in _format(args.artifact_id, hops, args.to):
        print(line)
    if unresolved:
        for u in sorted(set(unresolved)):
            print(f"UNRESOLVED: {u}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
