"""Unit tests for sdd_doc_lint TH-RES-001 (threshold-resolution gate).

CLEANUP-PR-D item 16. Each downstream `@threshold: PRD.NN.<cat>.<key>`
citation must resolve to a `full_id:` entry in the host PRD's
`component_decomposition` section.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Add the framework's tools/ dir to path so sdd_doc_lint resolves to canonical
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from sdd_doc_lint import _check_threshold_resolution  # noqa: E402


class ThresholdResolution(unittest.TestCase):
    """TH-RES-001: cross-document threshold resolution."""

    def test_pass_when_full_id_declared(self) -> None:
        """PRD declares full_id; BDD cites it → no finding."""
        prd_text = """---
doc_id: PRD-01
artifact_type: PRD
layer: 2
---
## 7b. Component Decomposition

component_decomposition:
  components:
    - id: "redirect-handler"
      thresholds:
        - key: "redirectp95"
          full_id: "PRD.01.perf.redirectp95"
          value: 200
"""
        bdd_text = """---
doc_id: BDD-01
artifact_type: BDD
---
Given a request within @threshold: PRD.01.perf.redirectp95
"""
        corpus = [
            ("docs/02_PRD/PRD-01.md", prd_text),
            ("docs/04_BDD/BDD-01.md", bdd_text),
        ]
        findings = _check_threshold_resolution(corpus)
        self.assertEqual([str(f) for f in findings], [], "expected no findings")

    def test_p2_when_prd_lacks_section(self) -> None:
        """BDD cites threshold but host PRD has no decomposition section."""
        prd_text = """---
doc_id: PRD-01
artifact_type: PRD
layer: 2
---
## 7. Scope

No component decomposition here.
"""
        bdd_text = "@threshold: PRD.01.perf.redirectp95"
        corpus = [
            ("docs/02_PRD/PRD-01.md", prd_text),
            ("docs/04_BDD/BDD-01.md", bdd_text),
        ]
        findings = _check_threshold_resolution(corpus)
        self.assertEqual(len(findings), 1, "expected 1 finding for missing section")
        self.assertEqual(findings[0].code, "TH-RES-001")
        self.assertIn("missing `component_decomposition`", findings[0].message)

    def test_p1_when_section_missing_key(self) -> None:
        """PRD has decomposition but cited threshold not declared."""
        prd_text = """---
doc_id: PRD-01
---
component_decomposition:
  components:
    - id: "redirect-handler"
      thresholds:
        - full_id: "PRD.01.perf.redirectp95"
          value: 200
"""
        bdd_text = "@threshold: PRD.01.perf.differentkey"
        corpus = [
            ("docs/02_PRD/PRD-01.md", prd_text),
            ("docs/04_BDD/BDD-01.md", bdd_text),
        ]
        findings = _check_threshold_resolution(corpus)
        self.assertEqual(len(findings), 1)
        self.assertIn("unresolved", findings[0].message)
        self.assertEqual(findings[0].path, "docs/04_BDD/BDD-01.md")

    def test_multi_prd_cross_resolution(self) -> None:
        """Citation for PRD-02 looks only at PRD-02's decomposition, not PRD-01's."""
        prd1 = """---
doc_id: PRD-01
---
component_decomposition:
  components:
    - id: "x"
      thresholds:
        - full_id: "PRD.01.perf.foo"
"""
        prd2 = """---
doc_id: PRD-02
---
## 7. Scope

No decomposition.
"""
        bdd_text = "@threshold: PRD.02.perf.bar"
        corpus = [
            ("docs/02_PRD/PRD-01.md", prd1),
            ("docs/02_PRD/PRD-02.md", prd2),
            ("docs/04_BDD/BDD-01.md", bdd_text),
        ]
        findings = _check_threshold_resolution(corpus)
        # Exactly 1 finding for PRD-02; PRD-01 is irrelevant
        self.assertEqual(len(findings), 1)
        self.assertIn("PRD-02", findings[0].message)


if __name__ == "__main__":
    unittest.main()
