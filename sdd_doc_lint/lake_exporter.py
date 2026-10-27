"""Central Federated Read Lake Exporter for SDD Graphs.

Projects local edge SDD graphs into standardized openCypher DDL/DML batches
and PostgreSQL 18 + Apache AGE SQL scripts.
Governed by docs/FEDERATED_READ_LAKE_PATTERN.md and
framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md (CHG-110, GD-97).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sdd_doc_lint.graph_engine import SddGraph


class CentralLakeExporter:
    """Projects SddGraph instances to Central Federated Read Lake dialects."""

    def __init__(self, tenant_id: str = "aidoc-framework") -> None:
        """Initialize exporter with a tenant repository slug."""
        self.tenant_id = tenant_id.strip().lstrip("@")

    def format_node_id(self, node_id: str) -> str:
        """Ensure node ID is namespaced with @tenant_id: prefix for cross-repo isolation."""
        if node_id.startswith("@"):
            return node_id
        return f"@{self.tenant_id}:{node_id}"

    def export_cypher(self, graph: SddGraph) -> str:
        """Generate openCypher script for Memgraph or Neo4j central lake ingestion."""
        lines: list[str] = [
            "// =====================================================================",
            "// Exported for Central Federated Read Lake (Memgraph / Neo4j)",
            f"// Tenant: @{self.tenant_id} | Nodes: {len(graph.nodes)} | Edges: {len(graph.edges)}",
            "// =====================================================================",
            "",
        ]

        # 1. Merge Nodes
        lines.append("// --- 1. Nodes ---")
        for nid, node in sorted(graph.nodes.items()):
            ntype = node.get("type", "sdd_node")
            target_id = self.format_node_id(nid)
            title = self._escape_str(str(node.get("title", "")))
            statement = self._escape_str(str(node.get("statement", "")))

            props_pairs = [
                f"n.title = '{title}'",
                f"n.statement = '{statement}'",
                f"n.tenant = '{self.tenant_id}'",
                f"n.raw_id = '{self._escape_str(nid)}'",
            ]

            # Additional node properties
            props = node.get("properties")
            if isinstance(props, dict):
                for k, v in sorted(props.items()):
                    if isinstance(v, (str, int, float, bool)):
                        props_pairs.append(f"n.{k} = '{self._escape_str(str(v))}'")

            set_clause = ", ".join(props_pairs)
            lines.append(f"MERGE (n:{ntype} {{id: '{target_id}'}}) SET {set_clause};")

        lines.append("")
        lines.append("// --- 2. Relationships ---")

        # 2. Merge Edges
        for edge in graph.edges:
            rel = edge["relation"]
            from_id = self.format_node_id(edge["from"])
            to_id = self.format_node_id(edge["to"])
            notes = self._escape_str(edge.get("notes", ""))

            notes_set = f" SET r.notes = '{notes}'" if notes else ""
            lines.append(
                f"MATCH (a {{id: '{from_id}'}}), (b {{id: '{to_id}'}}) "
                f"MERGE (a)-[r:{rel}]->(b){notes_set};"
            )

        return "\n".join(lines) + "\n"

    def export_age_sql(self, graph: SddGraph, graph_name: str = "aidoc_graph") -> str:
        """Generate PostgreSQL 18 + Apache AGE SQL script for production lake ingestion."""
        lines: list[str] = [
            "-- =====================================================================",
            "-- Exported for Central Federated Read Lake (PostgreSQL 18 + Apache AGE)",
            f"-- Tenant: @{self.tenant_id} | Graph: {graph_name}",
            "-- =====================================================================",
            "LOAD 'age';",
            'SET search_path = ag_catalog, "$user", public;',
            f"SELECT create_graph('{graph_name}') WHERE NOT EXISTS (SELECT 1 FROM ag_graph WHERE name = '{graph_name}');",
            "",
            "-- --- 1. Nodes ---",
        ]

        for nid, node in sorted(graph.nodes.items()):
            ntype = node.get("type", "sdd_node")
            target_id = self.format_node_id(nid)
            title = self._escape_str(str(node.get("title", "")))
            statement = self._escape_str(str(node.get("statement", "")))

            cypher_inner = (
                f"MERGE (n:{ntype} {{id: '{target_id}'}}) "
                f"SET n.title = '{title}', n.statement = '{statement}', n.tenant = '{self.tenant_id}'"
            )
            lines.append(
                f"SELECT * FROM cypher('{graph_name}', $$ {cypher_inner} $$) as (v agtype);"
            )

        lines.append("")
        lines.append("-- --- 2. Relationships ---")

        for edge in graph.edges:
            rel = edge["relation"]
            from_id = self.format_node_id(edge["from"])
            to_id = self.format_node_id(edge["to"])

            cypher_inner = (
                f"MATCH (a {{id: '{from_id}'}}), (b {{id: '{to_id}'}}) MERGE (a)-[r:{rel}]->(b)"
            )
            lines.append(
                f"SELECT * FROM cypher('{graph_name}', $$ {cypher_inner} $$) as (v agtype);"
            )

        return "\n".join(lines) + "\n"

    def export_bolt_payload(self, graph: SddGraph) -> dict[str, Any]:
        """Generate JSON-serializable dictionary for programmatic Bolt driver push."""
        nodes = []
        for nid, node in graph.nodes.items():
            nodes.append(
                {
                    "id": self.format_node_id(nid),
                    "raw_id": nid,
                    "type": node.get("type", "sdd_node"),
                    "title": node.get("title", ""),
                    "statement": node.get("statement", ""),
                    "tenant": self.tenant_id,
                    "properties": node.get("properties", {}),
                }
            )

        edges = []
        for edge in graph.edges:
            edges.append(
                {
                    "from": self.format_node_id(edge["from"]),
                    "to": self.format_node_id(edge["to"]),
                    "relation": edge["relation"],
                    "notes": edge.get("notes", ""),
                    "description": edge.get("description", ""),
                    "rationale": edge.get("rationale", ""),
                }
            )

        return {
            "tenant_id": self.tenant_id,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
        }

    def _escape_str(self, val: str) -> str:
        """Escape single quotes and newlines for Cypher string literals."""
        return val.replace("'", "\\'").replace("\n", " ").strip()
