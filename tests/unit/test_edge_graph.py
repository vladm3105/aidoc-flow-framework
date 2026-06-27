"""Unit: the net-new bidirectional element edge-graph (CFB-PR-2 DD-1 / R-c).

`_check_trace_resolution` computes citation adjacency per-line and discards it;
forward coverage needs it retained. `build_edge_graph` keeps every UPSTREAM
`@<layer>:` citation as a TraceEdge, so forward (cited→citers) and backward
(citer→cited) adjacency both derive from one structure. Downstream
forward-reference tags are excluded, matching the necessary-upstream contract
(strictly-downstream skip, same as the resolution check).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root  # noqa: E402

sys.path.insert(0, str(plugin_bundle_root()))
from sdd_doc_lint import build_edge_graph  # noqa: E402


def _doc(doc_id: str, artifact_type: str, body: str) -> tuple[str, str]:
    rel = f"{doc_id}.md"
    text = f"---\ndoc_id: {doc_id}\nartifact_type: {artifact_type}\n---\n\n{body}\n"
    return (rel, text)


# BRD-01 declares an FR element; PRD-01 cites it element-level; SPEC-01 cites
# BRD doc-level + an upstream EARS; the BRD also carries a stray downstream
# `@spec:` forward reference that must NOT become an upstream edge.
CORPUS = [
    _doc(
        "BRD-01",
        "BRD",
        "- **BRD.01.07.6c3f — Submit** (P1): a requirement.\n"
        "Forward ref to @spec: SPEC-01 (downstream — not an upstream edge).",
    ),
    _doc(
        "PRD-01",
        "PRD",
        "Realises @brd: BRD.01.07.6c3f via component decomposition.\n"
        "Element PRD.01.09.aaaa covers it.",
    ),
    _doc(
        "SPEC-01",
        "SPEC",
        "Traces @ears: EARS.01.03.bbbb and @brd: BRD-01 (doc-level lineage).",
    ),
]


class BuildEdgeGraph(unittest.TestCase):
    def setUp(self):
        self.g = build_edge_graph(CORPUS)

    def test_element_host_indexes_declarations_only(self):
        # FR declared in its host BRD.
        self.assertEqual(self.g.element_host.get("BRD.01.07.6c3f"), "BRD-01")
        self.assertEqual(self.g.element_host.get("PRD.01.09.aaaa"), "PRD-01")
        # A *cited* element is not declared by the citer — PRD cites BRD's FR
        # but does not host it.
        self.assertNotIn("BRD-01", {self.g.element_host.get("BRD.01.07.6c3f")} - {"BRD-01"})

    def test_doc_layer_mapping(self):
        self.assertEqual(self.g.doc_layer["PRD-01"], "PRD")
        self.assertEqual(self.g.doc_layer["SPEC-01"], "SPEC")

    def test_forward_citers_of_element(self):
        # The FR is cited (forward) by PRD-01 only.
        self.assertEqual(self.g.citers_of("BRD.01.07.6c3f"), {"PRD-01"})

    def test_forward_citers_of_doc_aggregates_element_and_doc_level(self):
        # BRD-01 is reached forward by PRD-01 (via its FR element) and SPEC-01
        # (via the doc-level @brd: BRD-01 tag).
        self.assertEqual(self.g.citers_of_doc("BRD-01"), {"PRD-01", "SPEC-01"})

    def test_downstream_forward_reference_is_not_an_upstream_edge(self):
        # BRD-01's stray `@spec: SPEC-01` is strictly downstream → no edge, so
        # SPEC-01 is not "cited by" BRD-01.
        self.assertNotIn("BRD-01", self.g.citers_of("SPEC-01"))
        self.assertEqual(self.g.citers_of_doc("SPEC-01"), set())

    def test_citers_in_layer(self):
        self.assertEqual(self.g.citers_in_layer("BRD.01.07.6c3f", "PRD"), {"PRD-01"})
        self.assertEqual(self.g.citers_in_layer("BRD.01.07.6c3f", "SPEC"), set())


class MultiBrdOrGroup(unittest.TestCase):
    def test_pipe_separated_multi_brd_yields_an_edge_each(self):
        # DD-8: `@brd: X | @brd: Y` parses as two citations → two edges.
        corpus = [
            _doc("BRD-01", "BRD", "- **BRD.01.07.aaaa — A** (P1): x."),
            _doc("BRD-02", "BRD", "- **BRD.02.07.bbbb — B** (P1): y."),
            _doc(
                "PRD-01",
                "PRD",
                "Realises @brd: BRD.01.07.aaaa | @brd: BRD.02.07.bbbb together.",
            ),
        ]
        g = build_edge_graph(corpus)
        self.assertEqual(g.citers_of("BRD.01.07.aaaa"), {"PRD-01"})
        self.assertEqual(g.citers_of("BRD.02.07.bbbb"), {"PRD-01"})


class IndexAndEmpty(unittest.TestCase):
    def test_index_docs_emit_no_edges(self):
        corpus = [
            _doc("BRD-01", "BRD", "- **BRD.01.07.aaaa — A** (P1): x."),
            _doc("PRD-00", "PRD-INDEX", "Index citing @brd: BRD.01.07.aaaa (informational)."),
        ]
        g = build_edge_graph(corpus)
        self.assertEqual(g.citers_of("BRD.01.07.aaaa"), set())

    def test_docs_without_doc_id_are_skipped(self):
        g = build_edge_graph([("loose.md", "no frontmatter, @brd: BRD-01 here")])
        self.assertEqual(g.edges, ())


if __name__ == "__main__":
    unittest.main()
