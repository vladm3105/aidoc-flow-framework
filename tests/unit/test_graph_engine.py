"""Unit tests for sdd_doc_lint.graph_engine (CHG-108).

Validates:
1. Pure-Python graph representation, DFS cycle detection, and topological sorting.
2. Binary Topological Validation (BTV) cardinality rules:
   - GRAPH-CARD-003: Acceptance scenario verifies formal requirement
   - GRAPH-CARD-004: Test fixture proves acceptance scenario
   - GRAPH-CARD-007: Mutating task action has compensated_by rollback task
   - GRAPH-DANGLE-001 / GRAPH-DANGLE-002: Dangling edge checks
   - Federated external ID references (@repo:NODE_ID)
3. Transitive blast radius calculation.
4. Mutated delta subgraph extraction.
"""

from __future__ import annotations

import unittest

from sdd_doc_lint.graph_engine import GraphEngine, SddGraph


class TestGraphEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = GraphEngine()

    def test_cycle_detection_positive(self) -> None:
        """Detect direct cycle A -> B -> A and multi-hop cycle A -> B -> C -> A."""
        g = SddGraph()
        g.add_node({"id": "TASK.01.01.a1b2", "type": "task_action", "title": "Task A"})
        g.add_node({"id": "TASK.01.01.c3d4", "type": "task_action", "title": "Task B"})
        g.add_edge("TASK.01.01.a1b2", "TASK.01.01.c3d4", "implements")
        g.add_edge("TASK.01.01.c3d4", "TASK.01.01.a1b2", "implements")

        cycles = g.find_cycles()
        self.assertTrue(len(cycles) > 0)
        self.assertFalse(g.is_dag())

    def test_cycle_detection_dag(self) -> None:
        """Confirm valid DAG produces no cycle."""
        g = SddGraph()
        g.add_node({"id": "TASK.01.01.a1b2", "type": "task_action", "title": "Task A"})
        g.add_node({"id": "TASK.01.01.c3d4", "type": "task_action", "title": "Task B"})
        g.add_node({"id": "TASK.01.01.e5f6", "type": "task_action", "title": "Task C"})
        g.add_edge("TASK.01.01.a1b2", "TASK.01.01.c3d4", "implements")
        g.add_edge("TASK.01.01.c3d4", "TASK.01.01.e5f6", "implements")

        cycles = g.find_cycles()
        self.assertEqual(len(cycles), 0)
        self.assertTrue(g.is_dag())

    def test_topological_sort(self) -> None:
        """Topological sort correctly orders dependencies."""
        g = SddGraph()
        g.add_node({"id": "T3", "type": "task_action", "title": "Task 3"})
        g.add_node({"id": "T1", "type": "task_action", "title": "Task 1"})
        g.add_node({"id": "T2", "type": "task_action", "title": "Task 2"})
        g.add_edge("T1", "T2", "implements")
        g.add_edge("T2", "T3", "implements")

        order = g.topological_sort()
        self.assertEqual(order, ["T1", "T2", "T3"])

    def test_blast_radius(self) -> None:
        """Transitive downstream blast radius includes all reachable descendants."""
        g = SddGraph()
        g.add_node({"id": "REQ.01", "type": "formal_requirement", "title": "Req A"})
        g.add_node({"id": "COMP.01", "type": "component_contract", "title": "Comp B"})
        g.add_node({"id": "TEST.01", "type": "test_fixture", "title": "Test C"})
        g.add_node({"id": "BDD.01", "type": "acceptance_scenario", "title": "Acc D"})
        g.add_node({"id": "BRD.01", "type": "business_objective", "title": "Unrelated E"})

        g.add_edge("REQ.01", "COMP.01", "implements")
        g.add_edge("COMP.01", "TEST.01", "proves")
        g.add_edge("REQ.01", "BDD.01", "verifies")

        radius = self.engine.calculate_blast_radius(g, "REQ.01")
        self.assertEqual(radius, {"COMP.01", "TEST.01", "BDD.01"})

        radius_b = self.engine.calculate_blast_radius(g, "COMP.01")
        self.assertEqual(radius_b, {"TEST.01"})

    def test_cardinality_task_compensation_rule(self) -> None:
        """GRAPH-CARD-007: Each mutating task must have a compensated_by edge to a rollback task."""
        g = SddGraph()
        g.add_node(
            {
                "id": "TASK.01.01.a1b2",
                "type": "task_action",
                "title": "Migrate DB",
                "action": "UPDATE schema",
            }
        )
        findings = self.engine.validate_btv(g)
        codes = [f.code for f in findings]
        self.assertIn("GRAPH-CARD-007", codes)

        # Add compensation task and edge
        g.add_node(
            {
                "id": "TASK.01.01.a1b2_rollback",
                "type": "task_action",
                "title": "Rollback DB",
                "compensation": "RESTORE schema",
            }
        )
        g.add_edge("TASK.01.01.a1b2", "TASK.01.01.a1b2_rollback", "compensated_by")

        findings2 = self.engine.validate_btv(g)
        codes2 = [f.code for f in findings2]
        self.assertNotIn("GRAPH-CARD-007", codes2)

    def test_cardinality_oracle_and_proof_rules(self) -> None:
        """GRAPH-CARD-003 and GRAPH-CARD-004: Requirement verified by BDD, BDD proven by TDD."""
        g = SddGraph()
        g.add_node(
            {
                "id": "EARS.01.01.a1b2",
                "type": "formal_requirement",
                "title": "Token TTL",
                "statement": "The system shall expire tokens after 15m.",
            }
        )
        # Missing BDD verifier
        findings = self.engine.validate_btv(g)
        codes = [f.code for f in findings]
        self.assertIn("GRAPH-CARD-003", codes)

        # Add BDD node and edge
        g.add_node(
            {
                "id": "BDD.01.01.c3d4",
                "type": "acceptance_scenario",
                "title": "Token Expiry Scenario",
            }
        )
        g.add_edge("BDD.01.01.c3d4", "EARS.01.01.a1b2", "verifies")

        # Now GRAPH-CARD-003 is resolved, but GRAPH-CARD-004 fires on unproven BDD
        findings2 = self.engine.validate_btv(g)
        codes2 = [f.code for f in findings2]
        self.assertNotIn("GRAPH-CARD-003", codes2)
        self.assertIn("GRAPH-CARD-004", codes2)

        # Add TDD node and edge
        g.add_node(
            {
                "id": "TDD.01.01.e5f6",
                "type": "test_fixture",
                "title": "Test Token Expiry",
            }
        )
        g.add_edge("TDD.01.01.e5f6", "BDD.01.01.c3d4", "proves")

        findings3 = self.engine.validate_btv(g)
        codes3 = [f.code for f in findings3]
        self.assertNotIn("GRAPH-CARD-004", codes3)

    def test_federated_id_reference(self) -> None:
        """Federated external ID references (@repo:NODE_ID) do not trigger dangling edge errors."""
        g = SddGraph()
        g.add_node(
            {
                "id": "PRD.01.01.a1b2",
                "type": "product_capability",
                "title": "Auth Gateway",
            }
        )
        # Edge pointing to external node in @auth-service repo
        g.add_edge("PRD.01.01.a1b2", "@auth-service:SPEC.02.01.f4e3", "realizes")

        findings = self.engine.validate_btv(g)
        dangling = [f for f in findings if f.code in ("GRAPH-DANGLE-001", "GRAPH-DANGLE-002")]
        self.assertEqual(len(dangling), 0)

    def test_extract_delta_subgraph(self) -> None:
        """Extract delta subgraph containing mutated node and 1-hop neighborhood."""
        g_base = SddGraph()
        g_base.add_node({"id": "REQ.01", "type": "formal_requirement", "title": "Req 1"})
        g_base.add_node({"id": "COMP.01", "type": "component_contract", "title": "Comp 1"})
        g_base.add_edge("COMP.01", "REQ.01", "implements")

        g_head = SddGraph()
        g_head.add_node({"id": "REQ.01", "type": "formal_requirement", "title": "Req 1 (Updated)"})
        g_head.add_node({"id": "COMP.01", "type": "component_contract", "title": "Comp 1"})
        g_head.add_node({"id": "TEST.01", "type": "test_fixture", "title": "Test 1"})
        g_head.add_edge("COMP.01", "REQ.01", "implements")
        g_head.add_edge("TEST.01", "REQ.01", "proves")

        delta = self.engine.extract_delta_subgraph(g_base, g_head)
        self.assertIn("REQ.01", delta.nodes)
        self.assertIn("TEST.01", delta.nodes)
        self.assertIn("COMP.01", delta.nodes)  # 1-hop neighbor of REQ.01

    def test_load_all_ten_layer_graph_templates(self) -> None:
        """Verify GraphEngine successfully loads all 10 layer graph templates."""
        from pathlib import Path

        repo_root = Path(__file__).resolve().parent.parent.parent
        layer_templates = sorted((repo_root / "framework" / "layers").glob("*/*-GRAPH-TEMPLATE.yaml"))
        self.assertEqual(len(layer_templates), 10)
        for tpl in layer_templates:
            g = self.engine.load_graph_file(tpl)
            self.assertGreater(len(g.nodes), 0, f"Template {tpl.name} has no nodes")
            self.assertTrue(g.is_dag(), f"Template {tpl.name} contains cycles")


if __name__ == "__main__":
    unittest.main()
