"""Unit tests for Embedded Kùzu Acceleration Adapter.

Verifies KuzuGraphAdapter behavior both when Kùzu is unavailable (pure-Python fallback)
and when mocked/installed.
Governed by framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md and
docs/FEDERATED_READ_LAKE_PATTERN.md (CHG-110, GD-97).
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from sdd_doc_lint.graph_engine import SddGraph
from sdd_doc_lint.kuzu_adapter import (
    NODE_TABLE_SCHEMAS,
    REL_TABLE_SCHEMAS,
    KuzuGraphAdapter,
)


class TestKuzuAdapterFallback(unittest.TestCase):
    """Test fallback and guardrails when Kùzu is not installed in the environment."""

    def test_availability_flag(self) -> None:
        """Verify is_available returns a bool matching runtime state."""
        self.assertIsInstance(KuzuGraphAdapter.is_available(), bool)

    @patch("sdd_doc_lint.kuzu_adapter.KUZU_AVAILABLE", False)
    def test_uninstalled_runtime_error(self) -> None:
        """Verify that attempting operations when Kùzu is absent raises informative RuntimeError."""
        adapter = KuzuGraphAdapter()
        self.assertFalse(adapter.is_connected)
        with self.assertRaises(RuntimeError) as ctx:
            adapter.init_schema()
        self.assertIn("pip install kuzu", str(ctx.exception))
        self.assertIn("pure-Python SddGraph", str(ctx.exception))

        with self.assertRaises(RuntimeError):
            adapter.query("MATCH (n) RETURN n")

        with self.assertRaises(RuntimeError):
            g = SddGraph()
            adapter.ingest_graph(g)


class TestKuzuAdapterMocked(unittest.TestCase):
    """Test schema initialization, ingestion, and query logic using mocked Kùzu driver."""

    def setUp(self) -> None:
        self.mock_kuzu = MagicMock()
        self.mock_db = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_kuzu.Database.return_value = self.mock_db
        self.mock_kuzu.Connection.return_value = self.mock_conn

    def test_init_schema_ddl_execution(self) -> None:
        """Verify that init_schema executes all 12 node tables and 9 rel tables."""
        with (
            patch("sdd_doc_lint.kuzu_adapter.kuzu", self.mock_kuzu),
            patch("sdd_doc_lint.kuzu_adapter.KUZU_AVAILABLE", True),
        ):
            adapter = KuzuGraphAdapter(":memory:")
            self.assertTrue(adapter.is_connected)
            adapter.init_schema()

            # 12 node tables + 9 rel tables = 21 DDL statements
            expected_calls = len(NODE_TABLE_SCHEMAS) + len(REL_TABLE_SCHEMAS)
            self.assertEqual(self.mock_conn.execute.call_count, expected_calls)

    def test_ingest_graph_and_query(self) -> None:
        """Verify that ingest_graph correctly creates nodes and edges in Kùzu."""
        g = SddGraph()
        g.add_node(
            {
                "id": "BRD.01.01.0001",
                "type": "business_objective",
                "title": "Revenue Growth",
                "statement": "Increase subscription revenue by 25%",
                "properties": {"priority": "P0"},
            }
        )
        g.add_node(
            {
                "id": "PRD.02.01.0001",
                "type": "product_capability",
                "title": "One-Click Checkout",
                "statement": "Enable frictionless one-click purchases",
                "properties": {"persona": "Shopper"},
            }
        )
        g.add_edge("PRD.02.01.0001", "BRD.01.01.0001", "realizes")

        with (
            patch("sdd_doc_lint.kuzu_adapter.kuzu", self.mock_kuzu),
            patch("sdd_doc_lint.kuzu_adapter.KUZU_AVAILABLE", True),
        ):
            adapter = KuzuGraphAdapter()
            counts = adapter.ingest_graph(g)
            self.assertEqual(counts["nodes"], 2)
            self.assertEqual(counts["edges"], 1)

            # Test query
            mock_query_result = MagicMock()
            mock_query_result.get_column_names.return_value = ["id", "title"]
            mock_query_result.has_next.side_effect = [True, False]
            mock_query_result.get_next.return_value = ["BRD.01.01.0001", "Revenue Growth"]
            self.mock_conn.execute.return_value = mock_query_result

            rows = adapter.query("MATCH (n:business_objective) RETURN n.id AS id, n.title AS title")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["id"], "BRD.01.01.0001")
            self.assertEqual(rows[0]["title"], "Revenue Growth")

    def test_ingest_system_container_and_decomposes_to(self) -> None:
        """Verify that system_container nodes with properties and multi-hop decomposes_to ingest properly."""
        g = SddGraph()
        g.add_node(
            {
                "id": "SEED-domain",
                "type": "seed_intent",
                "title": "Core Domain",
                "statement": "Domain strategic vision",
            }
        )
        g.add_node(
            {
                "id": "MODULE-01",
                "type": "system_container",
                "title": "Auth Service",
                "context": "Authentication and authorization container",
                "properties": {
                    "container_archetype": "api_service",
                    "trust_boundary": "DMZ",
                    "data_classification": "RESTRICTED",
                },
            }
        )
        g.add_node(
            {
                "id": "SPEC.06.01.0001",
                "type": "component_contract",
                "title": "OAuth Token Endpoint",
                "statement": "POST /oauth/token contract",
            }
        )
        g.add_edge("SEED-domain", "MODULE-01", "decomposes_to")
        g.add_edge("MODULE-01", "SPEC.06.01.0001", "decomposes_to")

        with (
            patch("sdd_doc_lint.kuzu_adapter.kuzu", self.mock_kuzu),
            patch("sdd_doc_lint.kuzu_adapter.KUZU_AVAILABLE", True),
        ):
            adapter = KuzuGraphAdapter()
            counts = adapter.ingest_graph(g)
            self.assertEqual(counts["nodes"], 3)
            self.assertEqual(counts["edges"], 2)

            # Verify system_container execute call carried properties
            calls = self.mock_conn.execute.call_args_list
            container_call = [c for c in calls if "n:system_container" in str(c)]
            self.assertEqual(len(container_call), 1)
            params = container_call[0][0][1]
            self.assertEqual(params["id"], "MODULE-01")
            self.assertEqual(params["container_archetype"], "api_service")
            self.assertEqual(params["trust_boundary"], "DMZ")
            self.assertEqual(params["data_classification"], "RESTRICTED")

    def test_ingest_evaluation_suite_and_verifies_edges(self) -> None:
        """Verify that evaluation_suite nodes and multi-target verifies edges ingest properly."""
        g = SddGraph()
        g.add_node(
            {
                "id": "EVAL.10.01.0001",
                "type": "evaluation_suite",
                "title": "E2E Verification Suite",
                "statement": "Verifies all requirements and tasks",
                "properties": {
                    "eval_track": "functional",
                    "environment": "staging",
                },
            }
        )
        g.add_node(
            {
                "id": "TASK.08.01.0001",
                "type": "task_action",
                "title": "Implement auth handler",
                "target_file": "src/auth.py",
            }
        )
        g.add_node(
            {
                "id": "TDD.07.01.0001",
                "type": "test_fixture",
                "title": "Test auth handler",
                "target_file": "tests/test_auth.py",
            }
        )
        g.add_node(
            {
                "id": "EARS.03.01.0001",
                "type": "formal_requirement",
                "title": "Ubiquitous audit log",
                "statement": "The system shall log all auth events.",
            }
        )
        g.add_edge("EVAL.10.01.0001", "TASK.08.01.0001", "verifies")
        g.add_edge("EVAL.10.01.0001", "TDD.07.01.0001", "verifies")
        g.add_edge("EVAL.10.01.0001", "EARS.03.01.0001", "verifies")

        with (
            patch("sdd_doc_lint.kuzu_adapter.kuzu", self.mock_kuzu),
            patch("sdd_doc_lint.kuzu_adapter.KUZU_AVAILABLE", True),
        ):
            adapter = KuzuGraphAdapter()
            counts = adapter.ingest_graph(g)
            self.assertEqual(counts["nodes"], 4)
            self.assertEqual(counts["edges"], 3)

            calls = self.mock_conn.execute.call_args_list
            eval_call = [c for c in calls if "n:evaluation_suite" in str(c)]
            self.assertEqual(len(eval_call), 1)
            params = eval_call[0][0][1]
            self.assertEqual(params["id"], "EVAL.10.01.0001")
            self.assertEqual(params["eval_track"], "functional")
            self.assertEqual(params["environment"], "staging")

            # Mock query for verifies edges
            mock_query_result = MagicMock()
            mock_query_result.get_column_names.return_value = ["eval_id", "task_id"]
            mock_query_result.has_next.side_effect = [True, False]
            mock_query_result.get_next.return_value = ["EVAL.10.01.0001", "TASK.08.01.0001"]
            self.mock_conn.execute.return_value = mock_query_result

            rows = adapter.query(
                "MATCH (e:evaluation_suite)-[:verifies]->(t:task_action) "
                "RETURN e.id AS eval_id, t.id AS task_id"
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["eval_id"], "EVAL.10.01.0001")
            self.assertEqual(rows[0]["task_id"], "TASK.08.01.0001")


if __name__ == "__main__":
    unittest.main()
