"""Phase 2a: governance admission + section-anchor parsing in the slicer.

A GOV-<STEM> front-matter doc parses to a document node whose `##` sections
with `{#sec-...}` anchors become addressable element nodes. Layer-chain
behavior is unchanged: a TYPE-NN doc without anchors still parses exactly
as before.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sdd_doc_lint.slice import SddGraph

GOV_DOC = """---
doc_id: GOV-EXAMPLE
bucket: normative-prose
authority: doc-leads
consumers: [authoring, audit]
---

# Example Governance Doc

## Selector {#sec-selector}

Classify first.

## Gates {#sec-gates}

Gate text.
"""

LAYER_DOC = """# BRD-01

## Business Objectives

Body text.
"""


class TestGovSliceAdmission(unittest.TestCase):
    def _graph(self, files):
        tmp = TemporaryDirectory()
        root = Path(tmp.name)
        for name, text in files.items():
            (root / name).write_text(text, encoding="utf-8")
        graph = SddGraph(root)
        tmp.cleanup()
        return graph

    def test_gov_doc_admitted_with_section_elements(self):
        graph = self._graph({"GOV-EXAMPLE.md": GOV_DOC})
        self.assertIn("GOV-EXAMPLE", graph.nodes)
        self.assertEqual(graph.nodes["GOV-EXAMPLE"].layer, "GOV")
        self.assertIn("GOV-EXAMPLE#sec-selector", graph.nodes)
        self.assertIn("GOV-EXAMPLE#sec-gates", graph.nodes)
        self.assertEqual(graph.nodes["GOV-EXAMPLE#sec-selector"].title, "Selector")

    def test_layer_doc_without_anchors_unchanged(self):
        graph = self._graph({"BRD-01.md": LAYER_DOC})
        self.assertIn("BRD-01", graph.nodes)
        self.assertEqual(graph.nodes["BRD-01"].layer, "BRD")
        self.assertEqual([n for n in graph.nodes if n.startswith("BRD-01#")], [])


if __name__ == "__main__":
    unittest.main()
