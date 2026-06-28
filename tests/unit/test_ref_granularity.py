"""Unit: the ref-granularity lint `REFGRAN01` (CFB-PR-3, GD-03).

A trace citation to an element-declaring layer (BRD/PRD/EARS/BDD/ADR/TDD) must be
element-level (`TYPE.NN.SS.xxxx`), not document-level (`TYPE-NN`). `@spec`/
`@iplan` are exempt (those layers declare no canonical elements). Self-tags +
downstream forward-pointers are excluded (the `build_edge_graph` edge set the
check reuses already drops them). Run-mode severity: warning in `build`, error
in `gate-code`.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root  # noqa: E402

sys.path.insert(0, str(plugin_bundle_root()))
from sdd_doc_lint import _check_ref_granularity, lint_path  # noqa: E402


def _doc(doc_id: str, artifact_type: str, body: str) -> tuple[str, str]:
    return (
        f"{doc_id}.md",
        f"---\ndoc_id: {doc_id}\nartifact_type: {artifact_type}\n---\n\n{body}\n",
    )


class RefGranularity(unittest.TestCase):
    def test_doc_level_upstream_ref_to_element_declaring_layer_flags(self):
        # BDD-01 cites @ears: EARS-01 (doc-level, EARS is upstream + element-declaring).
        corpus = [
            _doc("EARS-01", "EARS", "- EARS.01.03.aaaa: a requirement."),
            _doc("BDD-01", "BDD", "@ears: EARS-01\nScenario."),
        ]
        findings = _check_ref_granularity(corpus, "gate-code")
        self.assertEqual([(f.code, f.severity) for f in findings], [("REFGRAN01", "error")])
        self.assertIn("EARS-01", findings[0].message)

    def test_element_level_ref_is_silent(self):
        corpus = [
            _doc("EARS-01", "EARS", "- EARS.01.03.aaaa: a requirement."),
            _doc("BDD-01", "BDD", "@ears: EARS.01.03.aaaa\nScenario."),
        ]
        self.assertEqual(_check_ref_granularity(corpus), [])

    def test_spec_and_iplan_targets_are_exempt(self):
        # @spec / @iplan doc-level refs are correct (those layers declare no elements).
        corpus = [
            _doc("SPEC-01", "SPEC", "a spec"),
            _doc("TDD-01", "TDD", "@spec: SPEC-01\n- TDD.01.04.aaaa: a test."),
        ]
        self.assertEqual(_check_ref_granularity(corpus), [])

    def test_self_tags_and_downstream_pointers_excluded(self):
        # BDD-01 self-tag (@bdd: BDD-01) + EARS-01 downstream pointer (@bdd: BDD-01,
        # BDD is downstream of EARS) — neither is an upstream trace citation.
        corpus = [
            _doc("EARS-01", "EARS", "@bdd: BDD-01\n- EARS.01.03.aaaa: a req."),
            _doc("BDD-01", "BDD", "@bdd: BDD-01\n@ears: EARS.01.03.aaaa\nScenario."),
        ]
        self.assertEqual(_check_ref_granularity(corpus), [])

    def test_run_mode_severity(self):
        corpus = [
            _doc("EARS-01", "EARS", "- EARS.01.03.aaaa: a req."),
            _doc("BDD-01", "BDD", "@ears: EARS-01\nScenario."),
        ]
        self.assertEqual([f.severity for f in _check_ref_granularity(corpus, "build")], ["warning"])
        self.assertEqual(
            [f.severity for f in _check_ref_granularity(corpus, "gate-code")], ["error"]
        )

    def test_no_double_fire_only_refgran01(self):
        # A doc-level @ears: EARS-01 passes ID01 (valid doc form) + resolves under
        # TRACE-RES-001 (EARS-01 exists) → REFGRAN01 is the SOLE new finding.
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            for rel, text in [
                _doc("EARS-01", "EARS", "- EARS.01.03.aaaa: a req."),
                _doc("BDD-01", "BDD", "@ears: EARS-01\nScenario."),
            ]:
                (tdp / rel).write_text(text, encoding="utf-8")
            codes = {f.code for f in lint_path(tdp, mode="gate-code") if "EARS-01" in f.message}
            self.assertEqual(codes, {"REFGRAN01"})


if __name__ == "__main__":
    unittest.main()
