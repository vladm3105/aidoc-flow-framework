"""Unit: the backward coverage gate `COV02` (CFB-PR-2b).

The dual of `COV01`: every EARS/BDD requirement doc must transitively reach a
SPEC or TDD doc downstream (document-level binding; PR-3 refines to element
granularity). Escapes nothing — at doc level the only failure is a requirements
doc realized by nothing. Gated to corpora with a REAL (non-`-00`) SPEC/TDD doc
(DD-2b-3); run-mode severity (warning/`build`, error/`gate-code`).
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root  # noqa: E402

sys.path.insert(0, str(plugin_bundle_root()))
from sdd_doc_lint import _check_backward_coverage, lint_path  # noqa: E402


def _doc(doc_id: str, artifact_type: str, body: str) -> tuple[str, str]:
    return (
        f"{doc_id}.md",
        f"---\ndoc_id: {doc_id}\nartifact_type: {artifact_type}\n---\n\n{body}\n",
    )


def _req(doc_id: str, artifact_type: str, elem: str) -> tuple[str, str]:
    """A requirement doc that DECLARES one element (so element_host enumerates it)."""
    return _doc(doc_id, artifact_type, f"## 3. Requirements\n\n- {elem}: a requirement.")


def _real_spec(doc_id="SPEC-01", cites=None) -> tuple[str, str]:
    body = "\n".join(f"@{c.split('-')[0].lower()}: {c}" for c in (cites or []))
    return _doc(doc_id, "SPEC", body or "a spec.")


class GateRunsOnlyOnRealDesignTest(unittest.TestCase):
    def test_no_spec_tdd_in_corpus_is_noop(self):
        corpus = [_req("EARS-01", "EARS", "EARS.01.03.aaaa")]
        self.assertEqual(_check_backward_coverage(corpus), [])

    def test_bare_top_level_doc_id_spec00_index_does_not_activate(self):
        # V4: a SPEC-00 index authored WITH a top-level doc_id (layer resolves to
        # SPEC) must NOT activate the gate — the `-00` guard excludes it. Without
        # the guard, EARS-01 (reaching no real SPEC) would wrongly flag.
        corpus = [
            _req("EARS-01", "EARS", "EARS.01.03.aaaa"),
            _doc("SPEC-00", "SPEC", "bare index, cites nothing"),
        ]
        self.assertEqual(_check_backward_coverage(corpus), [])


class BackwardCoverage(unittest.TestCase):
    def test_covered_ears_doc_has_no_finding(self):
        # SPEC-01 cites EARS-01 → EARS-01 reaches SPEC → covered.
        corpus = [
            _req("EARS-01", "EARS", "EARS.01.03.aaaa"),
            _real_spec("SPEC-01", cites=["EARS-01"]),
        ]
        self.assertEqual(_check_backward_coverage(corpus), [])

    def test_covered_transitively_through_bdd(self):
        # EARS-01 ← BDD-01 ← SPEC-01: EARS reaches SPEC transitively.
        corpus = [
            _req("EARS-01", "EARS", "EARS.01.03.aaaa"),
            _doc("BDD-01", "BDD", "@ears: EARS-01\nScenario.\n- BDD.01.03.bbbb: a scenario."),
            _real_spec("SPEC-01", cites=["BDD-01"]),
        ]
        self.assertEqual(_check_backward_coverage(corpus), [])

    def test_uncovered_requirement_doc_flags_cov02(self):
        # EARS-01 declares an element but nothing downstream cites it; a real
        # disconnected SPEC-99 activates the gate.
        corpus = [
            _req("EARS-01", "EARS", "EARS.01.03.aaaa"),
            _real_spec("SPEC-99"),  # real, present, but does not cite EARS-01
        ]
        findings = _check_backward_coverage(corpus, "gate-code")
        self.assertEqual([(f.code, f.severity) for f in findings], [("COV02", "error")])
        self.assertIn("EARS-01", findings[0].message)

    def test_run_mode_severity(self):
        corpus = [_req("BDD-01", "BDD", "BDD.01.03.aaaa"), _real_spec("SPEC-99")]
        self.assertEqual(
            [f.severity for f in _check_backward_coverage(corpus, "build")], ["warning"]
        )
        self.assertEqual(
            [f.severity for f in _check_backward_coverage(corpus, "gate-code")], ["error"]
        )

    def test_index_docs_without_elements_are_not_checked(self):
        # EARS-00 declares no elements → not enumerated → never flagged, even
        # though a real SPEC is present.
        corpus = [
            _doc("EARS-00", "EARS", "index, no element declarations"),
            _real_spec("SPEC-01", cites=["EARS-00"]),
        ]
        self.assertEqual(_check_backward_coverage(corpus), [])


class LintPathWiring(unittest.TestCase):
    def _cov2(self, findings):
        return [f for f in findings if f.code == "COV02"]

    def test_wired_and_skippable(self):
        corpus = [_req("EARS-01", "EARS", "EARS.01.03.aaaa"), _real_spec("SPEC-99")]
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            for rel, text in corpus:
                (tdp / rel).write_text(text, encoding="utf-8")
            self.assertEqual(
                [f.severity for f in self._cov2(lint_path(tdp, mode="build"))], ["warning"]
            )
            self.assertEqual(self._cov2(lint_path(tdp, mode="gate-code", skip_coverage=True)), [])


if __name__ == "__main__":
    unittest.main()
