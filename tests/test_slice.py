"""Unit tests for sdd_doc_lint/slice.py (Minimal Context Slicing Engine).

Part of Phase 2 of plans/TOPOLOGICAL-VALIDATION-AND-SLICING-PLAN.md (CHG-98).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sdd_doc_lint.slice import (
    SddGraph,
    format_json,
    format_markdown,
    format_yaml,
    slice_graph,
)

FIXTURE_ROOT = (
    Path(__file__).resolve().parent / "acceptance" / "fixtures" / "fullpath" / "golden_chain"
)


class TestSddSliceEngine(unittest.TestCase):
    """Test suite for SddGraph and slice_graph topological extraction."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = SddGraph(FIXTURE_ROOT)

    def test_fixture_graph_loaded(self) -> None:
        """Verify that golden chain documents and elements are parsed into nodes."""
        self.assertIn("BRD-01", self.graph.nodes)
        self.assertIn("BRD.01.07.aaaa", self.graph.nodes)
        self.assertIn("PRD-01", self.graph.nodes)
        self.assertIn("PRD.01.09.aaaa", self.graph.nodes)
        self.assertIn("EARS-01", self.graph.nodes)
        self.assertIn("EARS.01.03.aaaa", self.graph.nodes)
        self.assertIn("BDD-01", self.graph.nodes)
        self.assertIn("BDD.01.03.bbbb", self.graph.nodes)
        self.assertIn("TDD-01", self.graph.nodes)
        self.assertIn("TDD.01.04.cccc", self.graph.nodes)

    def test_slice_upstream_pruning(self) -> None:
        """Upstream slice from TDD case isolates exact causal chain and prunes siblings."""
        nodes, edges = slice_graph(self.graph, "TDD.01.04.cccc", direction="upstream")
        node_ids = {n.id for n in nodes}

        # Causal ancestors MUST be present
        self.assertIn("TDD.01.04.cccc", node_ids)
        self.assertIn("BDD.01.03.bbbb", node_ids)
        self.assertIn("EARS.01.03.aaaa", node_ids)
        self.assertIn("PRD.01.09.aaaa", node_ids)
        self.assertIn("BRD.01.07.aaaa", node_ids)
        self.assertIn("SPEC-01", node_ids)

        # Unreferenced sibling elements MUST be pruned
        self.assertNotIn("EARS.01.03.cccc", node_ids)
        self.assertNotIn("BDD.01.03.cccc", node_ids)
        self.assertNotIn("BDD.01.03.dddd", node_ids)
        self.assertNotIn("BDD.01.03.eeee", node_ids)
        self.assertNotIn("TDD.01.04.dddd", node_ids)
        self.assertNotIn("TDD.01.04.eeee", node_ids)

    def test_slice_downstream(self) -> None:
        """Downstream slice from EARS requirement includes only citing scenarios and tests."""
        nodes, edges = slice_graph(self.graph, "EARS.01.03.cccc", direction="downstream")
        node_ids = {n.id for n in nodes}

        self.assertIn("EARS.01.03.cccc", node_ids)
        self.assertIn("BDD.01.03.eeee", node_ids)
        # Sibling BDD scenarios that cite EARS.01.03.aaaa or bbbb must NOT be present
        self.assertNotIn("BDD.01.03.bbbb", node_ids)
        self.assertNotIn("BDD.01.03.dddd", node_ids)

    def test_slice_bidirectional(self) -> None:
        """Bidirectional slice includes both ancestors and descendants."""
        nodes, edges = slice_graph(self.graph, "EARS.01.03.aaaa", direction="both")
        node_ids = {n.id for n in nodes}

        # Upstream ancestors
        self.assertIn("BRD.01.07.aaaa", node_ids)
        self.assertIn("PRD.01.09.aaaa", node_ids)
        # Downstream descendants
        self.assertIn("BDD.01.03.bbbb", node_ids)
        self.assertIn("TDD.01.04.cccc", node_ids)

    def test_depth_limiting(self) -> None:
        """Depth limit bounds graph traversal distance."""
        nodes_all, _ = slice_graph(self.graph, "TDD.01.04.cccc", direction="upstream", depth=None)
        nodes_depth_1, _ = slice_graph(self.graph, "TDD.01.04.cccc", direction="upstream", depth=1)

        self.assertGreater(len(nodes_all), len(nodes_depth_1))
        depth_1_ids = {n.id for n in nodes_depth_1}
        # Immediate parents
        self.assertIn("BDD.01.03.bbbb", depth_1_ids)
        self.assertIn("SPEC-01", depth_1_ids)
        # 2nd-degree ancestors should NOT be included
        self.assertNotIn("BRD.01.07.aaaa", depth_1_ids)
        self.assertNotIn("PRD.01.09.aaaa", depth_1_ids)

    def test_cycle_resilience(self) -> None:
        """Graph with circular citations terminates cleanly without infinite loops."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            f1 = tmp_path / "EARS-01.md"
            f1.write_text(
                "# EARS-01\n\n### EARS.01.01.aaaa\nStatement 1\n- @bdd: BDD.01.01.bbbb\n",
                encoding="utf-8",
            )
            f2 = tmp_path / "BDD-01.md"
            f2.write_text(
                "# BDD-01\n\n### BDD.01.01.bbbb\nScenario 1\n- @ears: EARS.01.01.aaaa\n",
                encoding="utf-8",
            )

            cyclic_graph = SddGraph(tmp_path)
            nodes, edges = slice_graph(cyclic_graph, "EARS.01.01.aaaa", direction="upstream")
            node_ids = {n.id for n in nodes}
            self.assertIn("EARS.01.01.aaaa", node_ids)
            self.assertIn("BDD.01.01.bbbb", node_ids)
            self.assertEqual(len(nodes), 4)  # 2 elements + 2 host documents

    def test_target_not_found_raises(self) -> None:
        """Unknown target raises KeyError."""
        with self.assertRaises(KeyError):
            slice_graph(self.graph, "NON_EXISTENT_ID")

    def test_format_json(self) -> None:
        """JSON output is valid JSON adhering to node and edge schemas."""
        nodes, edges = slice_graph(self.graph, "EARS.01.03.aaaa", direction="upstream")
        json_str = format_json("EARS.01.03.aaaa", "upstream", None, nodes, edges)
        data = json.loads(json_str)

        self.assertEqual(data["target"], "EARS.01.03.aaaa")
        self.assertEqual(data["direction"], "upstream")
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertTrue(len(data["nodes"]) > 0)

    def test_format_yaml(self) -> None:
        """YAML output serializes hierarchical slice correctly."""
        nodes, edges = slice_graph(self.graph, "EARS.01.03.aaaa", direction="upstream")
        yaml_str = format_yaml("EARS.01.03.aaaa", "upstream", None, nodes, edges)
        self.assertIn("target: EARS.01.03.aaaa", yaml_str)
        self.assertIn("slice:", yaml_str)
        self.assertIn("doc_id: BRD-01", yaml_str)

    def test_format_markdown(self) -> None:
        """Markdown output includes title, metadata, mermaid graph, and element details."""
        nodes, edges = slice_graph(self.graph, "EARS.01.03.aaaa", direction="upstream")
        md_str = format_markdown("EARS.01.03.aaaa", "upstream", None, nodes, edges)
        self.assertIn("# Topological Slice: `EARS.01.03.aaaa`", md_str)
        self.assertIn("```mermaid", md_str)
        self.assertIn("graph TD", md_str)
        self.assertIn("## Sliced Elements by Layer", md_str)

    def test_cli_execution(self) -> None:
        """CLI invocation via subprocess succeeds with exit code 0."""
        cmd = [
            sys.executable,
            "-m",
            "sdd_doc_lint.slice",
            "--target",
            "TDD.01.04.cccc",
            "--docs-root",
            str(FIXTURE_ROOT),
            "--direction",
            "upstream",
            "--format",
            "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        data = json.loads(result.stdout)
        self.assertEqual(data["target"], "TDD.01.04.cccc")

    def test_cli_file_output(self) -> None:
        """CLI writes to output file when -o is specified."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            cmd = [
                sys.executable,
                "-m",
                "sdd_doc_lint.slice",
                "--target",
                "EARS.01.03.aaaa",
                "--docs-root",
                str(FIXTURE_ROOT),
                "-o",
                str(tmp_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0)
            content = tmp_path.read_text(encoding="utf-8")
            self.assertIn("target: EARS.01.03.aaaa", content)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
