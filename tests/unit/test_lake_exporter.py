"""Unit tests for Central Federated Read Lake Exporter.

Verifies openCypher DDL/DML emission, PostgreSQL 18 + Apache AGE SQL wrappers,
and Bolt payload generation.
Governed by docs/FEDERATED_READ_LAKE_PATTERN.md (CHG-110, GD-97).
"""

from __future__ import annotations

import unittest

from sdd_doc_lint.graph_engine import SddGraph
from sdd_doc_lint.lake_exporter import CentralLakeExporter


class TestLakeExporter(unittest.TestCase):
    """Test suite for CentralLakeExporter."""

    def setUp(self) -> None:
        self.exporter = CentralLakeExporter(tenant_id="auth-core")
        self.graph = SddGraph()
        self.graph.add_node(
            {
                "id": "BRD.01.01.a1b2",
                "type": "business_objective",
                "title": "OAuth 2.1 Compliance",
                "statement": "Enforce strict PKCE and secure token flows.",
                "properties": {"priority": "P0"},
            }
        )
        self.graph.add_node(
            {
                "id": "SPEC.06.01.c3d4",
                "type": "component_contract",
                "title": "Token Issuer gRPC Service",
                "statement": "Issues and signs Ed25519 token pairs.",
                "properties": {"protocol": "grpc"},
            }
        )
        self.graph.add_edge(
            "SPEC.06.01.c3d4", "BRD.01.01.a1b2", "realizes", notes="Realizes security requirement"
        )

    def test_format_node_id_namespacing(self) -> None:
        """Verify node IDs are prepended with @tenant: if not already namespaced."""
        self.assertEqual(
            self.exporter.format_node_id("BRD.01.01.0001"),
            "@auth-core:BRD.01.01.0001",
        )
        # Already namespaced node should remain untouched
        self.assertEqual(
            self.exporter.format_node_id("@billing-service:SPEC.06.01.0001"),
            "@billing-service:SPEC.06.01.0001",
        )

    def test_export_cypher_memgraph_format(self) -> None:
        """Verify openCypher statement emission for Memgraph and Neo4j."""
        cypher = self.exporter.export_cypher(self.graph)
        self.assertIn("// Tenant: @auth-core", cypher)
        self.assertIn("MERGE (n:business_objective {id: '@auth-core:BRD.01.01.a1b2'})", cypher)
        self.assertIn("n.title = 'OAuth 2.1 Compliance'", cypher)
        self.assertIn("n.tenant = 'auth-core'", cypher)
        self.assertIn("MERGE (n:component_contract {id: '@auth-core:SPEC.06.01.c3d4'})", cypher)
        self.assertIn(
            "MATCH (a {id: '@auth-core:SPEC.06.01.c3d4'}), (b {id: '@auth-core:BRD.01.01.a1b2'})",
            cypher,
        )
        self.assertIn(
            "MERGE (a)-[r:realizes]->(b) SET r.notes = 'Realizes security requirement';", cypher
        )

    def test_export_age_sql_format(self) -> None:
        """Verify PostgreSQL 18 + Apache AGE SQL script generation."""
        sql = self.exporter.export_age_sql(self.graph, graph_name="enterprise_lake")
        self.assertIn("LOAD 'age';", sql)
        self.assertIn("SELECT create_graph('enterprise_lake')", sql)
        self.assertIn("SELECT * FROM cypher('enterprise_lake', $$ MERGE (n:business_objective", sql)
        self.assertIn("SELECT * FROM cypher('enterprise_lake', $$ MATCH (a", sql)

    def test_export_bolt_payload(self) -> None:
        """Verify structured Bolt JSON dictionary generation."""
        payload = self.exporter.export_bolt_payload(self.graph)
        self.assertEqual(payload["tenant_id"], "auth-core")
        self.assertEqual(payload["node_count"], 2)
        self.assertEqual(payload["edge_count"], 1)
        self.assertEqual(len(payload["nodes"]), 2)
        self.assertEqual(len(payload["edges"]), 1)

        node_ids = {n["id"] for n in payload["nodes"]}
        self.assertIn("@auth-core:BRD.01.01.a1b2", node_ids)
        self.assertIn("@auth-core:SPEC.06.01.c3d4", node_ids)

        edge = payload["edges"][0]
        self.assertEqual(edge["from"], "@auth-core:SPEC.06.01.c3d4")
        self.assertEqual(edge["to"], "@auth-core:BRD.01.01.a1b2")
        self.assertEqual(edge["relation"], "realizes")


if __name__ == "__main__":
    unittest.main()
