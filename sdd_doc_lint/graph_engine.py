"""Native SDD Graph Engine — pure stdlib + PyYAML graph verification and traversal.

Implements Binary Topological Validation (BTV), cycle detection, cardinality
invariants, blast-radius calculation, and delta extraction for autonomous AI agents.
Governed by framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md (CHG-108, GD-95).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# Canonical Node & Edge Types
NODE_TYPES = {
    "seed_intent",
    "system_container",
    "business_objective",
    "product_capability",
    "formal_requirement",
    "acceptance_scenario",
    "architectural_decision",
    "component_contract",
    "test_fixture",
    "task_action",
    "change_request",
    "evaluation_suite",
}

EDGE_RELATIONS = {
    "decomposes_to",
    "realizes",
    "verifies",
    "proves",
    "constrains",
    "implements",
    "compensated_by",
    "authorized_by",
    "supersedes",
}

# Regex for node IDs
PROD_ID_PATTERN = re.compile(
    r"^(@[a-zA-Z0-9_-]+:)?("
    r"[A-Z]{3,4}\.[0-9]{2}\.[0-9]{2}\.[a-f0-9]{4}"
    r"|TASK\.[0-9]{2}\.[0-9]{2}\.[a-f0-9]{4}(_rollback)?"
    r"|CHG-[0-9]{2,3}"
    r"|SEED-[a-zA-Z0-9_-]+"
    r"|MODULE-[0-9]{2})$"
)

TEMPLATE_ID_PATTERN = re.compile(
    r"^(@[a-zA-Z0-9_-]+:)?("
    r"[A-Z]{3,4}\.[0-9]{2}\.[0-9]{2}\.(xxxx|[a-f0-9]{4})"
    r"|TASK\.[0-9]{2}\.[0-9]{2}\.(xxxx|[a-f0-9]{4})(_rollback)?"
    r"|CHG-([0-9]{2,3}|NN)"
    r"|SEED-[a-zA-Z0-9_-]+"
    r"|MODULE-([0-9]{2}|NN))$"
)


@dataclass
class GraphFinding:
    """A structured finding emitted during graph validation."""

    code: str
    severity: str  # "error" | "warning" | "info"
    message: str
    node_id: str | None = None
    file_path: str | None = None


class SddGraph:
    """Pure-Python Directed Property Graph representing an SDD specification."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self.adj: dict[str, set[str]] = {}  # outgoing: from -> {to}
        self.pred: dict[str, set[str]] = {}  # incoming: to -> {from}
        self.slice_ids: set[str] = set()
        self.metadata: dict[str, Any] = {}

    def add_node(self, node: dict[str, Any], slice_id: str | None = None) -> None:
        nid = node["id"]
        self.nodes[nid] = node
        if slice_id:
            self.nodes[nid]["_slice_id"] = slice_id
        if nid not in self.adj:
            self.adj[nid] = set()
        if nid not in self.pred:
            self.pred[nid] = set()

    def add_edge(
        self,
        from_id: str,
        to_id: str,
        relation: str,
        notes: str | None = None,
        description: str | None = None,
        rationale: str | None = None,
        properties: dict[str, Any] | None = None,
        **extra: Any,
    ) -> None:
        edge: dict[str, Any] = {"from": from_id, "to": to_id, "relation": relation}
        if notes:
            edge["notes"] = notes
        if description:
            edge["description"] = description
        if rationale:
            edge["rationale"] = rationale
        if properties:
            edge["properties"] = properties
        for k, v in extra.items():
            if v is not None:
                edge[k] = v
        self.edges.append(edge)

        if from_id not in self.adj:
            self.adj[from_id] = set()
        self.adj[from_id].add(to_id)

        if to_id not in self.pred:
            self.pred[to_id] = set()
        self.pred[to_id].add(from_id)

    def is_dag(self) -> bool:
        """Return True if the graph is a Directed Acyclic Graph (DAG)."""
        return len(self.find_cycles()) == 0

    def extract_slice_subgraph(self, slice_id: str) -> SddGraph:
        """Extract nodes and edges belonging strictly to a specific slice_id."""
        sub = SddGraph()
        sub.slice_ids.add(slice_id)
        if self.metadata:
            sub.metadata.update(self.metadata)
        for nid, node in self.nodes.items():
            if node.get("_slice_id") == slice_id:
                sub.add_node(dict(node), slice_id=slice_id)
        for edge in self.edges:
            if edge["from"] in sub.nodes and edge["to"] in sub.nodes:
                edge_kwargs = {k: v for k, v in edge.items() if k not in ("from", "to", "relation")}
                sub.add_edge(edge["from"], edge["to"], edge["relation"], **edge_kwargs)
        return sub

    def find_cycles(self) -> list[list[str]]:
        """Detect and return all directed cycles using 3-color DFS."""
        visited: dict[str, int] = {}  # 0: unvisited, 1: visiting (in stack), 2: visited
        cycles: list[list[str]] = []
        stack: list[str] = []

        for node in self.nodes:
            visited[node] = 0

        def dfs(u: str) -> None:
            visited[u] = 1
            stack.append(u)
            for v in self.adj.get(u, set()):
                if v not in visited:
                    continue
                if visited[v] == 1:
                    # Cycle detected: backtrack to start of cycle
                    cycle_start = stack.index(v)
                    cycles.append(stack[cycle_start:] + [v])
                elif visited[v] == 0:
                    dfs(v)
            stack.pop()
            visited[u] = 2

        for node in list(self.nodes.keys()):
            if visited[node] == 0:
                dfs(node)

        return cycles

    def topological_sort(self) -> list[str]:
        """Return a topologically sorted list of node IDs (Kahn's algorithm)."""
        in_degree = {u: len(self.pred.get(u, set())) for u in self.nodes}
        queue = [u for u, deg in in_degree.items() if deg == 0]
        order: list[str] = []

        while queue:
            u = queue.pop(0)
            order.append(u)
            for v in self.adj.get(u, set()):
                if v in in_degree:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        queue.append(v)

        return order

    def descendants(self, node_id: str) -> set[str]:
        """Return all downstream reachable nodes (Blast Radius)."""
        result: set[str] = set()
        queue = list(self.adj.get(node_id, set()))
        while queue:
            curr = queue.pop(0)
            if curr not in result:
                result.add(curr)
                queue.extend(self.adj.get(curr, set()))
        return result

    def ancestors(self, node_id: str) -> set[str]:
        """Return all upstream source nodes."""
        result: set[str] = set()
        queue = list(self.pred.get(node_id, set()))
        while queue:
            curr = queue.pop(0)
            if curr not in result:
                result.add(curr)
                queue.extend(self.pred.get(curr, set()))
        return result

    def nodes_by_type(self, node_type: str) -> list[dict[str, Any]]:
        """Return all nodes of a specific type."""
        return [n for n in self.nodes.values() if n.get("type") == node_type]

    def to_kuzu(self, db_path: str | Path | None = None) -> Any:
        """Ingest this graph into an embedded Kùzu adapter instance (optional acceleration)."""
        from sdd_doc_lint.kuzu_adapter import KuzuGraphAdapter

        adapter = KuzuGraphAdapter(db_path=db_path)
        adapter.ingest_graph(self)
        return adapter

    def to_lake_cypher(self, tenant_id: str = "aidoc-framework") -> str:
        """Export this graph to openCypher DDL/DML for Central Federated Read Lake."""
        from sdd_doc_lint.lake_exporter import CentralLakeExporter

        return CentralLakeExporter(tenant_id=tenant_id).export_cypher(self)

    def to_lake_age(
        self, tenant_id: str = "aidoc-framework", graph_name: str = "aidoc_graph"
    ) -> str:
        """Export this graph to PostgreSQL 18 + Apache AGE SQL script."""
        from sdd_doc_lint.lake_exporter import CentralLakeExporter

        return CentralLakeExporter(tenant_id=tenant_id).export_age_sql(self, graph_name=graph_name)


def is_federated_stub(target_id: str) -> bool:
    """Return True if target_id is an external federated reference (@repo:ID)."""
    return target_id.startswith("@") and ":" in target_id


class GraphEngine:
    """Loads, validates, and queries Native SDD Property Graphs."""

    def load_slice_data(self, data: dict[str, Any], slice_id: str | None = None) -> SddGraph:
        """Parse raw dictionary into an SddGraph."""
        graph = SddGraph()
        sid = slice_id or data.get("slice_id", "ANONYMOUS_SLICE")
        graph.slice_ids.add(sid)
        if isinstance(data.get("metadata"), dict):
            graph.metadata.update(data["metadata"])

        for node in data.get("nodes", []):
            if isinstance(node, dict) and "id" in node:
                graph.add_node(node, slice_id=sid)

        for edge in data.get("edges", []):
            if isinstance(edge, dict) and "from" in edge and "to" in edge and "relation" in edge:
                from_id = edge["from"]
                to_id = edge["to"]
                rel = edge["relation"]
                edge_kwargs = {k: v for k, v in edge.items() if k not in ("from", "to", "relation")}
                graph.add_edge(from_id, to_id, rel, **edge_kwargs)

        return graph

    def load_graph_file(self, file_path: Path) -> SddGraph:
        """Load a single .graph.yaml file."""
        text = file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        return self.load_slice_data(data, slice_id=data.get("slice_id", file_path.stem))

    def load_graph_directory(self, dir_path: Path) -> SddGraph:
        """Load and merge all .graph.yaml files recursively under a directory."""
        unified = SddGraph()
        for p in sorted(dir_path.rglob("*.graph.yaml")):
            sub = self.load_graph_file(p)
            unified.slice_ids.update(sub.slice_ids)
            unified.metadata.update(sub.metadata)
            for nid, node in sub.nodes.items():
                unified.add_node(node, slice_id=node.get("_slice_id"))
            for edge in sub.edges:
                from_id = edge["from"]
                to_id = edge["to"]
                rel = edge["relation"]
                edge_kwargs = {k: v for k, v in edge.items() if k not in ("from", "to", "relation")}
                unified.add_edge(from_id, to_id, rel, **edge_kwargs)
        return unified

    def validate_btv(self, graph: SddGraph, is_template: bool = False) -> list[GraphFinding]:
        """Execute strict Binary Topological Validation (BTV)."""
        findings: list[GraphFinding] = []
        is_tpl = is_template or any("TEMPLATE" in s for s in graph.slice_ids)
        id_pattern = TEMPLATE_ID_PATTERN if is_tpl else PROD_ID_PATTERN

        # 1. Structural Checks on Nodes
        for nid, node in graph.nodes.items():
            if not id_pattern.match(nid):
                findings.append(
                    GraphFinding(
                        code="GRAPH-ID-001",
                        severity="error",
                        message=f"Malformed node ID format '{nid}'. Must match TYPE.NN.SS.xxxx.",
                        node_id=nid,
                    )
                )
            ntype = node.get("type")
            if ntype not in NODE_TYPES:
                findings.append(
                    GraphFinding(
                        code="GRAPH-TYPE-001",
                        severity="error",
                        message=f"Unrecognized node type '{ntype}' on node '{nid}'.",
                        node_id=nid,
                    )
                )

        # 2. Dangling Edge Resolution (Zero Dangling Pointers)
        for edge in graph.edges:
            src = edge["from"]
            tgt = edge["to"]
            rel = edge["relation"]

            if src not in graph.nodes and not is_federated_stub(src):
                findings.append(
                    GraphFinding(
                        code="GRAPH-DANGLE-001",
                        severity="error",
                        message=f"Dangling edge source '{src}' in relation '{rel}' -> '{tgt}'.",
                        node_id=src,
                    )
                )
            if tgt not in graph.nodes and not is_federated_stub(tgt):
                findings.append(
                    GraphFinding(
                        code="GRAPH-DANGLE-002",
                        severity="error",
                        message=f"Dangling edge target '{tgt}' in relation '{src}' -> '{rel}'.",
                        node_id=tgt,
                    )
                )
            if rel not in EDGE_RELATIONS:
                findings.append(
                    GraphFinding(
                        code="GRAPH-REL-001",
                        severity="error",
                        message=f"Unrecognized edge relation '{rel}' between '{src}' and '{tgt}'.",
                    )
                )

        # 3. Acyclicity (Strict DAG check)
        cycles = graph.find_cycles()
        for cyc in cycles:
            findings.append(
                GraphFinding(
                    code="GRAPH-CYCLE-001",
                    severity="error",
                    message=f"Directed cycle detected in SDD graph: {' -> '.join(cyc)}",
                )
            )

        # 4. Cardinality Invariants (Oracle Realization & Coverage)
        # GRAPH-CARD-001: Every seed_intent must decompose to >= 1 system_container or product_capability
        for seed in graph.nodes_by_type("seed_intent"):
            sid = seed["id"]
            decompositions = [
                tgt
                for tgt in graph.adj.get(sid, set())
                if any(
                    e["relation"] == "decomposes_to"
                    and e["from"] == sid
                    and e["to"] == tgt
                    and graph.nodes.get(tgt, {}).get("type")
                    in ("system_container", "product_capability")
                    for e in graph.edges
                )
            ]
            if not decompositions:
                findings.append(
                    GraphFinding(
                        code="GRAPH-CARD-001",
                        severity="error",
                        message=f"Seed vision failure: seed intent '{sid}' has 0 decomposing system containers or product capabilities.",
                        node_id=sid,
                    )
                )

        # GRAPH-CARD-003: Every formal_requirement must have >= 1 acceptance_scenario verifying it
        for req in graph.nodes_by_type("formal_requirement"):
            rid = req["id"]
            # Look for incoming edges with relation="verifies"
            verifiers = [
                src
                for src in graph.pred.get(rid, set())
                if any(e["relation"] == "verifies" and e["from"] == src for e in graph.edges)
            ]
            if not verifiers:
                findings.append(
                    GraphFinding(
                        code="GRAPH-CARD-003",
                        severity="error",
                        message=f"Oracle coverage failure: requirement '{rid}' has 0 verifying acceptance scenarios.",
                        node_id=rid,
                    )
                )

        # GRAPH-CARD-004: Every acceptance_scenario must have >= 1 test_fixture proving it
        for bdd in graph.nodes_by_type("acceptance_scenario"):
            bid = bdd["id"]
            provers = [
                src
                for src in graph.pred.get(bid, set())
                if any(e["relation"] == "proves" and e["from"] == src for e in graph.edges)
            ]
            if not provers:
                findings.append(
                    GraphFinding(
                        code="GRAPH-CARD-004",
                        severity="error",
                        message=f"Test proof failure: scenario '{bid}' has 0 proving test fixtures.",
                        node_id=bid,
                    )
                )

        # GRAPH-CARD-007: Every mutating task_action must have a compensated_by edge
        for task in graph.nodes_by_type("task_action"):
            tid = task["id"]
            if "_rollback" in tid:
                continue  # Rollback tasks do not require another rollback
            rollbacks = [
                tgt
                for tgt in graph.adj.get(tid, set())
                if any(e["relation"] == "compensated_by" and e["to"] == tgt for e in graph.edges)
            ]
            if not rollbacks:
                findings.append(
                    GraphFinding(
                        code="GRAPH-CARD-007",
                        severity="error",
                        message=f"Saga compensation failure: task action '{tid}' has 0 compensated_by rollback tasks.",
                        node_id=tid,
                    )
                )

        # GRAPH-CARD-010: Every evaluation_suite must verify >= 1 target (task_action, test_fixture, or formal_requirement)
        for suite in graph.nodes_by_type("evaluation_suite"):
            eid = suite["id"]
            verified_targets = [
                tgt
                for tgt in graph.adj.get(eid, set())
                if any(
                    e["relation"] == "verifies"
                    and e["from"] == eid
                    and e["to"] == tgt
                    and (
                        graph.nodes.get(tgt, {}).get("type")
                        in ("task_action", "test_fixture", "formal_requirement")
                        or is_federated_stub(tgt)
                    )
                    for e in graph.edges
                )
            ]
            if not verified_targets:
                findings.append(
                    GraphFinding(
                        code="GRAPH-CARD-010",
                        severity="error",
                        message=f"Evaluation coverage failure: evaluation suite '{eid}' has 0 verified targets (task_action, test_fixture, or formal_requirement).",
                        node_id=eid,
                    )
                )

        return findings

    def calculate_blast_radius(self, graph: SddGraph, node_id: str) -> set[str]:
        """Compute all downstream affected nodes from a mutated node."""
        if node_id not in graph.nodes:
            return set()
        return graph.descendants(node_id)

    def extract_delta_subgraph(self, base_graph: SddGraph, head_graph: SddGraph) -> SddGraph:
        """Extract only the mutated nodes plus immediate parents/children for AI PR review."""
        delta = SddGraph()
        changed_nodes: set[str] = set()

        # Added or modified nodes
        for nid, h_node in head_graph.nodes.items():
            if nid not in base_graph.nodes:
                changed_nodes.add(nid)
            elif h_node != base_graph.nodes[nid]:
                changed_nodes.add(nid)

        # Include immediate 1-hop neighborhood for context
        neighborhood: set[str] = set(changed_nodes)
        for nid in changed_nodes:
            neighborhood.update(head_graph.pred.get(nid, set()))
            neighborhood.update(head_graph.adj.get(nid, set()))

        # Build delta graph
        for nid in neighborhood:
            if nid in head_graph.nodes:
                delta.add_node(head_graph.nodes[nid])

        for edge in head_graph.edges:
            if edge["from"] in neighborhood and edge["to"] in neighborhood:
                delta.add_edge(edge["from"], edge["to"], edge["relation"], edge.get("notes"))

        return delta


def main(argv: list[str] | None = None) -> int:
    """CLI runner for GraphEngine BTV verification."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="python3 -m sdd_doc_lint.graph_engine",
        description="Validate SDD Graph slices against Binary Topological Validation (BTV) rules.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="One or more .graph.yaml files or directories to validate",
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="Validate in template mode (allows NN and xxxx wildcard placeholder tokens)",
    )
    args = parser.parse_args(argv)

    engine = GraphEngine()
    total_findings: list[GraphFinding] = []

    for path in args.paths:
        if not path.exists():
            print(f"Error: path does not exist: {path}", file=sys.stderr)
            return 2
        g = engine.load_graph_directory(path) if path.is_dir() else engine.load_graph_file(path)
        findings = engine.validate_btv(g, is_template=args.template)
        total_findings.extend(findings)

    errors = [f for f in total_findings if f.severity == "error"]
    for f in total_findings:
        stream = sys.stderr if f.severity == "error" else sys.stdout
        print(f"[{f.severity.upper()}] {f.code}: {f.message}", file=stream)

    if errors:
        print(f"\nBTV Validation Failed: {len(errors)} error(s) found.", file=sys.stderr)
        return 1
    print("BTV Validation Passed: 0 errors.")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
