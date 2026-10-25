#!/usr/bin/env python3
"""Minimal Context Slicing Engine for SDD Document Graphs.

Extracts deterministic upstream (ancestor) or downstream (descendant)
topological subgraphs for any target document or element ID, pruning
unreferenced sibling branches to prevent context bloat in autonomous AI agents.

Part of Phase 2 of plans/TOPOLOGICAL-VALIDATION-AND-SLICING-PLAN.md (CHG-98).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from sdd_doc_lint._common import yaml
    from sdd_doc_lint.trace_graph import (
        DOC_FORM,
        ELEM_FORM,
        LAYER_INDEX,
        TAG,
        doc_id_from_token,
        emit_tags,
    )
except ImportError:
    from _common import yaml
    from trace_graph import (
        DOC_FORM,
        ELEM_FORM,
        LAYER_INDEX,
        TAG,
        doc_id_from_token,
        emit_tags,
    )

#: Regex matching element headings: e.g. `### EARS.01.03.aaaa Login response`
_MD_HEADING_ELEM = re.compile(r"^#{2,4}\s+([A-Z]+\.\d+\.\d+\.[a-f0-9]+)(?:\s+(.*))?$")
#: Regex matching bold-prefixed element list items:
#: `- **BRD.01.07.aaaa — Authenticated session** (P1): ...`
#: `**ADR.01.03.a1b2** — Token-based authentication...`
_MD_BOLD_ELEM = re.compile(
    r"^[-*]?\s*\*\*([A-Z]+\.\d+\.\d+\.[a-f0-9]+)(?:\s*[—–-]\s*(.*?))?\*\*:?\s*(.*)$"
)
#: Any Markdown heading
_MD_ANY_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
#: Document heading: `# EARS-01`
_MD_DOC_HEADING = re.compile(r"^#\s+([A-Z]+-\d+)")
#: Governance front-matter doc id: `GOV-<STEM>` (Phase 2a structured Markdown)
_GOV_DOC = re.compile(r"^GOV-[A-Z0-9-]+$")
#: Governance section anchor: `## Title {#sec-slug}` (Phase 2a stable section IDs)
_MD_SECTION_ID = re.compile(r"^(#{2,6})\s+(.*?)\s*\{#([A-Za-z0-9_-]+)\}\s*$")
#: Standalone element pattern
_ELEM_PATTERN = re.compile(r"\b([A-Z]+)\.(\d+)\.(\d+)\.([a-f0-9]+)\b")


@dataclass
class SddNode:
    """A node in the SDD topological graph (document or element)."""

    id: str
    type: str  # "document" or "element"
    layer: str
    layer_n: int
    doc_id: str
    path: str
    title: str = ""
    statement: str = ""
    outgoing_tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "layer": self.layer,
            "layer_n": self.layer_n,
            "doc_id": self.doc_id,
            "path": self.path,
            "title": self.title,
            "statement": self.statement.strip(),
            "outgoing_tags": self.outgoing_tags,
        }


@dataclass
class SddEdge:
    """A directed edge in the topological graph (source depends on target)."""

    source: str
    target: str
    layer: str
    edge_type: str = "dependency"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "layer": self.layer,
            "edge_type": self.edge_type,
        }

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SddEdge):
            return False
        return self.source == other.source and self.target == other.target

    def __hash__(self) -> int:
        return hash((self.source, self.target))


class SddGraph:
    """Directed topological graph of SDD documents and elements."""

    def __init__(self, docs_root: Path) -> None:
        self.docs_root = docs_root
        self.nodes: dict[str, SddNode] = {}
        self.out_edges: dict[str, list[str]] = {}  # source -> [upstream targets]
        self.in_edges: dict[str, list[str]] = {}  # target -> [downstream sources]
        self.doc_elements: dict[str, list[str]] = {}  # doc_id -> [element_ids]
        self.element_doc: dict[str, str] = {}  # element_id -> doc_id
        self.build_graph()

    def add_node(self, node: SddNode) -> None:
        self.nodes[node.id] = node
        if node.type == "element":
            self.element_doc[node.id] = node.doc_id
            if node.id not in self.doc_elements.setdefault(node.doc_id, []):
                self.doc_elements[node.doc_id].append(node.id)

    def add_edge(self, source: str, target: str, layer: str, edge_type: str = "dependency") -> None:
        out_list = self.out_edges.setdefault(source, [])
        if target not in out_list:
            out_list.append(target)
        in_list = self.in_edges.setdefault(target, [])
        if source not in in_list:
            in_list.append(source)

    def build_graph(self) -> None:
        """Scan docs_root and extract all document and element nodes and edges."""
        if not self.docs_root.is_dir():
            return

        candidate_files: list[Path] = []
        for ext in ("*.md", "*.yaml", "*.yml"):
            candidate_files.extend(self.docs_root.rglob(ext))

        for file_path in sorted(candidate_files):
            rel = file_path.relative_to(self.docs_root)
            if any(part.startswith(".") for part in rel.parts):
                continue
            self._parse_file(file_path)

        # Wire edges based on outgoing_tags
        for source_id, node in list(self.nodes.items()):
            for raw_tag in node.outgoing_tags:
                clean_target = raw_tag.rstrip(".,:;!?)'\"")
                if clean_target == source_id:
                    continue
                if clean_target in self.nodes:
                    target_layer = self.nodes[clean_target].layer
                    self.add_edge(source_id, clean_target, target_layer)
                else:
                    doc_id = doc_id_from_token(clean_target)
                    layer = doc_id.split("-")[0] if doc_id else "UNKNOWN"
                    self.add_edge(source_id, clean_target, layer)

    def _parse_file(self, file_path: Path) -> None:
        rel_path = str(file_path.relative_to(self.docs_root))
        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError:
            return

        is_yaml = file_path.suffix.lower() in (".yaml", ".yml")
        if is_yaml:
            self._parse_yaml_file(file_path, rel_path, text)
        else:
            self._parse_markdown_file(file_path, rel_path, text)

    def _infer_doc_id(self, file_path: Path, text: str) -> tuple[str, str, int]:
        """Infer doc_id, layer name, and layer index from text and file path."""
        # 1. Frontmatter check
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm_text = parts[1]
                try:
                    fm = yaml.safe_load(fm_text) if yaml else None
                    if isinstance(fm, dict):
                        doc_id = str(
                            fm.get("doc_id") or fm.get("id") or fm.get("artifact_id") or ""
                        ).strip()
                        if DOC_FORM.match(doc_id):
                            layer = doc_id.split("-")[0]
                            return doc_id, layer, LAYER_INDEX.get(layer, 0)
                        # Governance admission (Phase 2a): GOV-<STEM> docs are
                        # addressable even though they match no layer chain.
                        if _GOV_DOC.match(doc_id):
                            return doc_id, "GOV", 0
                except Exception:
                    pass

        # 2. Markdown H1 check
        m_h1 = _MD_DOC_HEADING.search(text)
        if m_h1:
            doc_id = m_h1.group(1)
            layer = doc_id.split("-")[0]
            return doc_id, layer, LAYER_INDEX.get(layer, 0)

        # 3. Filename stem check
        stem = file_path.stem
        m_file = re.match(r"^([A-Z]+-\d+)", stem)
        if m_file:
            doc_id = m_file.group(1)
            layer = doc_id.split("-")[0]
            return doc_id, layer, LAYER_INDEX.get(layer, 0)

        # 4. Folder name fallback
        parent_name = file_path.parent.name
        m_folder = re.match(r"^\d+_([A-Z]+)$", parent_name)
        if m_folder:
            layer = m_folder.group(1)
            return f"{layer}-01", layer, LAYER_INDEX.get(layer, 0)

        return "", "", 0

    def _parse_markdown_file(self, file_path: Path, rel_path: str, text: str) -> None:
        doc_id, layer, layer_n = self._infer_doc_id(file_path, text)
        if not doc_id:
            return

        doc_tags = emit_tags(text)
        doc_node = SddNode(
            id=doc_id,
            type="document",
            layer=layer,
            layer_n=layer_n,
            doc_id=doc_id,
            path=rel_path,
            title=doc_id,
            statement="",
            outgoing_tags=doc_tags,
        )
        self.add_node(doc_node)

        lines = text.splitlines()
        elem_starts: list[
            tuple[int, str, str, str, str]
        ] = []  # (line_idx, elem_id, title, inline_stmt, kind)

        for idx, line in enumerate(lines):
            # Check governance section anchor (Phase 2a, GOV docs only)
            if layer == "GOV":
                ms = _MD_SECTION_ID.match(line)
                if ms:
                    title = ms.group(2).strip()
                    elem_id = f"{doc_id}#{ms.group(3)}"
                    elem_starts.append((idx, elem_id, title, "", "section"))
                    continue
            # Check Heading element
            mh = _MD_HEADING_ELEM.match(line)
            if mh:
                elem_id = mh.group(1)
                title = mh.group(2) or ""
                parts = elem_id.split(".")
                if len(parts) >= 2 and f"{parts[0]}-{parts[1]}" == doc_id:
                    elem_starts.append((idx, elem_id, title.strip(), "", "heading"))
                continue

            # Check Bold-prefixed element
            mb = _MD_BOLD_ELEM.match(line)
            if mb:
                elem_id = mb.group(1)
                title = mb.group(2) or ""
                rest = mb.group(3) or ""
                if not title and (
                    rest.startswith("—") or rest.startswith("–") or rest.startswith("-")
                ):
                    rest = rest.lstrip("—–- ").strip()
                    title_part, _, stmt_part = rest.partition(".")
                    if stmt_part:
                        title = title_part.strip()
                        rest = stmt_part.strip()
                    else:
                        title = rest
                        rest = ""
                parts = elem_id.split(".")
                if len(parts) >= 2 and f"{parts[0]}-{parts[1]}" == doc_id:
                    elem_starts.append((idx, elem_id, title.strip(), rest.strip(), "bold"))

        # Extract content & tags for each element
        for i, (start_idx, elem_id, title, inline_stmt, kind) in enumerate(elem_starts):
            if kind == "heading":
                end_idx = len(lines)
                for next_idx in range(start_idx + 1, len(lines)):
                    if _MD_ANY_HEADING.match(lines[next_idx]):
                        end_idx = next_idx
                        break
                elem_lines = lines[start_idx + 1 : end_idx]
            else:
                end_idx = len(lines)
                if i + 1 < len(elem_starts):
                    end_idx = elem_starts[i + 1][0]
                else:
                    for next_idx in range(start_idx + 1, len(lines)):
                        if _MD_ANY_HEADING.match(lines[next_idx]):
                            end_idx = next_idx
                            break
                elem_lines = [inline_stmt] + lines[start_idx + 1 : end_idx]

            elem_text = "\n".join(elem_lines).strip()
            elem_tags = emit_tags(elem_text)
            line_tags = emit_tags(lines[start_idx])
            for t in line_tags:
                if t not in elem_tags:
                    elem_tags.append(t)

            stmt_lines = [
                l for l in elem_lines if not TAG.search(l) and not l.strip().startswith("- @")
            ]
            statement = "\n".join(stmt_lines).strip()

            elem_node = SddNode(
                id=elem_id,
                type="element",
                layer=layer,
                layer_n=layer_n,
                doc_id=doc_id,
                path=rel_path,
                title=title,
                statement=statement,
                outgoing_tags=elem_tags,
            )
            self.add_node(elem_node)

    def _parse_yaml_file(self, file_path: Path, rel_path: str, text: str) -> None:
        doc_id, layer, layer_n = self._infer_doc_id(file_path, text)
        if not doc_id:
            return

        doc_tags = emit_tags(text)
        doc_node = SddNode(
            id=doc_id,
            type="document",
            layer=layer,
            layer_n=layer_n,
            doc_id=doc_id,
            path=rel_path,
            title=doc_id,
            statement="",
            outgoing_tags=doc_tags,
        )
        self.add_node(doc_node)

        docs_data: list[Any] = []
        try:
            if yaml:
                docs_data = [d for d in yaml.safe_load_all(text) if isinstance(d, dict)]
        except Exception:
            docs_data = []

        if docs_data:
            for d in docs_data:
                self._extract_yaml_elements(d, doc_id, layer, layer_n, rel_path)
        else:
            self._extract_yaml_elements_regex(doc_id, layer, layer_n, rel_path, text)

    def _extract_yaml_elements(
        self,
        data: Any,
        doc_id: str,
        layer: str,
        layer_n: int,
        rel_path: str,
    ) -> None:
        def walk(obj: Any) -> None:
            if isinstance(obj, dict):
                elem_id = ""
                for k in ("id", "elem_id", "case_id", "item_id"):
                    val = str(obj.get(k) or "").strip()
                    if ELEM_FORM.match(val):
                        elem_id = val
                        break

                if elem_id:
                    parts = elem_id.split(".")
                    if len(parts) >= 2 and f"{parts[0]}-{parts[1]}" == doc_id:
                        title = str(
                            obj.get("title")
                            or obj.get("name")
                            or obj.get("target")
                            or obj.get("contract")
                            or ""
                        ).strip()
                        statement = str(
                            obj.get("statement")
                            or obj.get("description")
                            or obj.get("contract")
                            or ""
                        ).strip()

                        obj_dump = yaml.dump(obj) if yaml else str(obj)
                        tags = emit_tags(obj_dump)

                        # Capture explicit references
                        for ref_key in (
                            "spec_ref",
                            "bdd_ref",
                            "adr_ref",
                            "ears_ref",
                            "prd_ref",
                            "brd_ref",
                        ):
                            ref_val = str(obj.get(ref_key) or "").strip()
                            clean_ref = ref_val.split(":")[-1].strip().rstrip(".,:;!?)'\"")
                            if clean_ref and (
                                DOC_FORM.match(clean_ref) or ELEM_FORM.match(clean_ref)
                            ):
                                if clean_ref not in tags:
                                    tags.append(clean_ref)

                        elem_node = SddNode(
                            id=elem_id,
                            type="element",
                            layer=layer,
                            layer_n=layer_n,
                            doc_id=doc_id,
                            path=rel_path,
                            title=title,
                            statement=statement,
                            outgoing_tags=tags,
                        )
                        self.add_node(elem_node)

                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)

        walk(data)

    def _extract_yaml_elements_regex(
        self,
        doc_id: str,
        layer: str,
        layer_n: int,
        rel_path: str,
        text: str,
    ) -> None:
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            for m in _ELEM_PATTERN.finditer(line):
                elem_id = m.group(0)
                parts = elem_id.split(".")
                if len(parts) >= 2 and f"{parts[0]}-{parts[1]}" == doc_id:
                    if elem_id not in self.nodes:
                        # Extract local lines around the element for tags
                        start_l = max(0, idx - 2)
                        end_l = min(len(lines), idx + 8)
                        local_text = "\n".join(lines[start_l:end_l])
                        elem_node = SddNode(
                            id=elem_id,
                            type="element",
                            layer=layer,
                            layer_n=layer_n,
                            doc_id=doc_id,
                            path=rel_path,
                            title=elem_id,
                            statement="",
                            outgoing_tags=emit_tags(local_text),
                        )
                        self.add_node(elem_node)


def slice_graph(
    graph: SddGraph,
    target: str,
    direction: str = "upstream",
    depth: int | None = None,
) -> tuple[list[SddNode], list[SddEdge]]:
    """Perform topological slicing from target node.

    Args:
        graph: The constructed SddGraph.
        target: Document ID or Element ID to start slicing from.
        direction: 'upstream' (ancestors), 'downstream' (descendants), or 'both'.
        depth: Max hop distance (None for unlimited).

    Returns:
        (nodes, edges) in the sliced subgraph.
    """
    clean_target = target.strip()
    if clean_target.startswith("@"):
        clean_target = clean_target.split(":", 1)[-1].strip()
    clean_target = clean_target.rstrip(".,:;!?)'\"")

    if clean_target not in graph.nodes:
        if clean_target not in graph.doc_elements:
            raise KeyError(f"Target '{clean_target}' not found in document graph")

    start_nodes = [clean_target]

    visited_nodes: set[str] = set()
    collected_edges: list[SddEdge] = []

    def get_neighbors(node_id: str, mode: str) -> list[str]:
        if mode == "upstream":
            return graph.out_edges.get(node_id, [])
        elif mode == "downstream":
            return graph.in_edges.get(node_id, [])
        return []

    # BFS queue: (node_id, current_depth, direction)
    queue: deque[tuple[str, int, str]] = deque()
    for s in start_nodes:
        visited_nodes.add(s)
        if direction in ("upstream", "both"):
            queue.append((s, 0, "upstream"))
        if direction in ("downstream", "both"):
            queue.append((s, 0, "downstream"))

    while queue:
        curr_id, curr_depth, current_dir = queue.popleft()
        if depth is not None and curr_depth >= depth:
            continue

        neighbors = get_neighbors(curr_id, current_dir)
        for nbr in neighbors:
            src = curr_id if current_dir == "upstream" else nbr
            dst = nbr if current_dir == "upstream" else curr_id
            layer = graph.nodes[dst].layer if dst in graph.nodes else "UNKNOWN"
            edge = SddEdge(source=src, target=dst, layer=layer)
            if edge not in collected_edges:
                collected_edges.append(edge)

            if nbr not in visited_nodes:
                visited_nodes.add(nbr)
                queue.append((nbr, curr_depth + 1, current_dir))

    # Also resolve host document node for included elements
    extra_docs: set[str] = set()
    for nid in list(visited_nodes):
        if nid in graph.element_doc:
            doc_id = graph.element_doc[nid]
            if doc_id in graph.nodes and doc_id not in visited_nodes:
                extra_docs.add(doc_id)
    visited_nodes.update(extra_docs)

    # Sort nodes topologically: layer_n ascending, then doc_id, then element id
    result_nodes = [graph.nodes[nid] for nid in visited_nodes if nid in graph.nodes]
    result_nodes.sort(key=lambda n: (n.layer_n, n.doc_id, n.type != "document", n.id))

    # Filter edges to only those connecting nodes in visited_nodes
    final_edges = [
        e for e in collected_edges if e.source in visited_nodes and e.target in visited_nodes
    ]

    return result_nodes, final_edges


def format_json(
    target: str,
    direction: str,
    depth: int | None,
    nodes: list[SddNode],
    edges: list[SddEdge],
) -> str:
    """Format slice results as structured JSON."""
    payload = {
        "target": target,
        "direction": direction,
        "depth": depth,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "nodes": [n.to_dict() for n in nodes],
        "edges": [e.to_dict() for e in edges],
    }
    return json.dumps(payload, indent=2)


def format_yaml(
    target: str,
    direction: str,
    depth: int | None,
    nodes: list[SddNode],
    edges: list[SddEdge],
) -> str:
    """Format slice results as concise hierarchical YAML."""
    docs_map: dict[str, dict[str, Any]] = {}

    for node in nodes:
        if node.type == "document":
            docs_map.setdefault(
                node.id,
                {
                    "doc_id": node.id,
                    "layer": node.layer,
                    "layer_index": node.layer_n,
                    "path": node.path,
                    "elements": [],
                },
            )
        elif node.type == "element":
            doc_entry = docs_map.setdefault(
                node.doc_id,
                {
                    "doc_id": node.doc_id,
                    "layer": node.layer,
                    "layer_index": node.layer_n,
                    "path": node.path,
                    "elements": [],
                },
            )
            elem_dict: dict[str, Any] = {"id": node.id}
            if node.title:
                elem_dict["title"] = node.title
            if node.statement:
                elem_dict["statement"] = node.statement
            active_out = [e.target for e in edges if e.source == node.id]
            if active_out:
                elem_dict["traces_to"] = active_out
            doc_entry["elements"].append(elem_dict)

    sorted_docs = sorted(docs_map.values(), key=lambda d: d.get("layer_index", 0))

    payload = {
        "target": target,
        "direction": direction,
        "depth": depth,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "slice": sorted_docs,
    }

    if yaml:
        return yaml.safe_dump(payload, sort_keys=False)
    return json.dumps(payload, indent=2)


def format_markdown(
    target: str,
    direction: str,
    depth: int | None,
    nodes: list[SddNode],
    edges: list[SddEdge],
) -> str:
    """Format slice results as human-readable Markdown."""
    lines: list[str] = []
    lines.append(f"# Topological Slice: `{target}`")
    lines.append("")
    lines.append(f"- **Direction:** `{direction}`")
    lines.append(f"- **Depth Limit:** `{depth if depth is not None else 'unlimited'}`")
    lines.append(f"- **Nodes Sliced:** `{len(nodes)}`")
    lines.append(f"- **Edges Preserved:** `{len(edges)}`")
    lines.append("")

    if edges:
        lines.append("## Causal Trace Graph")
        lines.append("")
        lines.append("```mermaid")
        lines.append("graph TD")
        for e in edges:
            lines.append(f'  "{e.source}" --> "{e.target}"')
        lines.append("```")
        lines.append("")

    lines.append("## Sliced Elements by Layer")
    lines.append("")

    current_layer = ""
    for node in nodes:
        if node.type == "document":
            continue
        if node.layer != current_layer:
            current_layer = node.layer
            lines.append(f"### Layer {node.layer_n}: {current_layer} ({node.doc_id})")
            lines.append("")

        lines.append(f"#### `{node.id}` {node.title}")
        lines.append(f"- **File:** `{node.path}`")
        if node.statement:
            lines.append(f"- **Contract Statement:**\n> {node.statement}")

        active_out = [e.target for e in edges if e.source == node.id]
        if active_out:
            lines.append(f"- **Upstream Targets:** {', '.join(f'`{t}`' for t in active_out)}")

        active_in = [e.source for e in edges if e.target == node.id]
        if active_in:
            lines.append(f"- **Downstream Dependents:** {', '.join(f'`{s}`' for s in active_in)}")
        lines.append("")

    return "\n".join(lines)


def auto_detect_docs_root() -> Path:
    """Search common SDD doc locations in workspace."""
    cwd = Path.cwd()
    for candidate in ("docs", "framework/layers", "framework", "."):
        p = cwd / candidate
        if p.is_dir() and any(p.glob("*_BRD")):
            return p
        if (p / "01_BRD").is_dir():
            return p
    fixture_dir = cwd / "tests/acceptance/fixtures/fullpath/golden_chain"
    if fixture_dir.is_dir():
        return fixture_dir
    return cwd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m sdd_doc_lint.slice",
        description="Extract minimal topological ancestor/descendant context slices.",
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        help="Target document ID (e.g. EARS-01) or element ID (e.g. EARS.01.03.aaaa).",
    )
    parser.add_argument(
        "-d",
        "--direction",
        choices=["upstream", "downstream", "both"],
        default="upstream",
        help="Traversal direction: upstream (ancestors), downstream (descendants), or both.",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=None,
        help="Maximum hop distance to traverse (default: unlimited).",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["yaml", "markdown", "json"],
        default="yaml",
        help="Output serialization format (default: yaml).",
    )
    parser.add_argument(
        "--docs-root",
        type=Path,
        default=None,
        help="Root path of the SDD documents tree (default: auto-detected).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Optional file path to write output slice (default: stdout).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    docs_root = args.docs_root or auto_detect_docs_root()
    if not docs_root.is_dir():
        print(f"Error: Documentation root '{docs_root}' does not exist.", file=sys.stderr)
        return 1

    graph = SddGraph(docs_root)
    if not graph.nodes:
        print(f"Error: No SDD documents found under '{docs_root}'.", file=sys.stderr)
        return 1

    try:
        nodes, edges = slice_graph(graph, args.target, args.direction, args.depth)
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.format == "json":
        output_text = format_json(args.target, args.direction, args.depth, nodes, edges)
    elif args.format == "markdown":
        output_text = format_markdown(args.target, args.direction, args.depth, nodes, edges)
    else:
        output_text = format_yaml(args.target, args.direction, args.depth, nodes, edges)

    if args.output:
        try:
            args.output.write_text(output_text, encoding="utf-8")
        except OSError as e:
            print(f"Error writing to {args.output}: {e}", file=sys.stderr)
            return 1
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
