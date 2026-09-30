"""Conformance: the CFB-PR-2 forward-coverage engine (gate + template rule).

Ties the engine to the spec contract at the conformance tier:

  * The forward-coverage gate (``COV01``) blocks an in-scope FR that reaches no
    SPEC and stays silent on a fully-covered cascade (DD-6), and is gated to
    whole-corpus runs (DD-1).
  * The BRD template carries the normative FR-annotation rule (DD-3/DD-4) the
    authored-artifact form depends on.

CLEANUP-001: the ``TRACEABILITY_MATRIX.md`` determinism half (V5) and the
example-corpus COV02 census retired with ``examples/url-shortener`` +
``tools/sdd_coverage.py``. The gate half below drives ``sdd_doc_lint``
directly, so it survives the framework-only reduction.
"""

import unittest

from _spec import FRAMEWORK

from sdd_doc_lint import (  # noqa: E402
    _check_backward_coverage,
    _check_forward_coverage,
    _check_phase_leak,
    _check_ref_granularity,
)


def _doc(doc_id: str, artifact_type: str, body: str) -> tuple[str, str]:
    return (
        f"{doc_id}.md",
        f"---\ndoc_id: {doc_id}\nartifact_type: {artifact_type}\n---\n\n{body}\n",
    )


class RetiredMatrixDeterminism(unittest.TestCase):
    """Retired with the corpus (CLEANUP-001): ``examples/url-shortener`` is gone.

    The determinism contract moves with the renderer; resurrect with it."""

    def test_example_corpus_is_gone(self) -> None:
        from _spec import REPO_ROOT

        self.assertFalse(
            (REPO_ROOT / "examples").exists(),
            "examples/ is back — resurrect MatrixDeterminism with _collect_corpus",
        )


class ForwardCoverageContract(unittest.TestCase):
    def _covered(self):
        # ELEMENT-COVERAGE-001: the PRD cites the BRD FR **element** (not the doc)
        # so element-level COV01 passes; the rest cite the upstream doc id.
        order = ["BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN"]
        brd = _doc(
            "BRD-01",
            "BRD",
            "## 7. Functional Requirements\n\n- **BRD.01.07.aaaa — F** (P1): a thing.",
        )
        corpus = [brd]
        for i in range(1, len(order)):
            up = order[i - 1]
            cite = "BRD.01.07.aaaa" if up == "BRD" else f"{up}-01"
            corpus.append(_doc(f"{order[i]}-01", order[i], f"@{up.lower()}: {cite}"))
        return corpus

    def test_fully_covered_cascade_has_no_cov01(self):
        self.assertEqual(_check_forward_coverage(self._covered()), [])

    def test_in_scope_fr_with_no_spec_blocks(self):
        # FR cited element-level by PRD (precedence (1) passes) but host reaches
        # no SPEC → the no-SPEC branch fires (ELEMENT-COVERAGE-001).
        corpus = [
            _doc(
                "BRD-01",
                "BRD",
                "## 7. Functional Requirements\n\n- **BRD.01.07.aaaa — F** (P1): x.",
            ),
            _doc("PRD-01", "PRD", "@brd: BRD.01.07.aaaa"),
            _doc("SPEC-99", "SPEC", "standalone"),
            _doc("IPLAN-99", "IPLAN", "standalone"),
        ]
        findings = _check_forward_coverage(corpus)
        self.assertEqual([(f.code, f.severity) for f in findings], [("COV01", "error")])
        self.assertIn("no SPEC", findings[0].message)

    def test_gated_to_whole_corpus_runs(self):
        # No SPEC/IPLAN in the corpus → the check no-ops (DD-1).
        brd = _doc(
            "BRD-01", "BRD", "## 7. Functional Requirements\n\n- **BRD.01.07.aaaa — F** (P1): x."
        )
        self.assertEqual(_check_forward_coverage([brd]), [])


class BackwardCoverageContract(unittest.TestCase):
    def test_retired_example_corpus_census(self) -> None:
        """Retired with the corpus (CLEANUP-001): ``examples/url-shortener`` is gone.

        The 16-orphan COV02 census codified the deleted corpus's known state;
        the gate half below carries the live contract. Resurrect the census
        with the corpus, per Decision 7 (drive over an in-tree fixture)."""
        from _spec import REPO_ROOT

        self.assertFalse(
            (REPO_ROOT / "examples").exists(),
            "examples/ is back — resurrect the example-corpus COV02 census",
        )

    def test_uncovered_requirement_doc_blocks_in_gate_code(self):
        corpus = [
            _doc("EARS-01", "EARS", "## 3. Requirements\n\n- EARS.01.03.aaaa: a req."),
            _doc("SPEC-99", "SPEC", "real spec, cites nothing"),
        ]
        findings = _check_backward_coverage(corpus, "gate-code")
        self.assertEqual([(f.code, f.severity) for f in findings], [("COV02", "error")])

    def test_gated_to_real_design_test_present(self):
        # No real (non-`-00`) SPEC/TDD → no-op (incl. a bare top-level-doc_id index).
        only_reqs = [_doc("EARS-01", "EARS", "## 3. Requirements\n\n- EARS.01.03.aaaa: a req.")]
        self.assertEqual(_check_backward_coverage(only_reqs), [])
        with_bare_index = only_reqs + [_doc("SPEC-00", "SPEC", "bare index")]
        self.assertEqual(_check_backward_coverage(with_bare_index), [])


class RefGranularityContract(unittest.TestCase):
    def test_doc_level_ref_to_element_declaring_layer_blocks_in_gate_code(self):
        corpus = [
            _doc("EARS-01", "EARS", "- EARS.01.03.aaaa: a req."),
            _doc("BDD-01", "BDD", "@ears: EARS-01\nScenario."),
        ]
        findings = _check_ref_granularity(corpus, "gate-code")
        self.assertEqual([(f.code, f.severity) for f in findings], [("REFGRAN01", "error")])

    def test_element_level_and_spec_iplan_targets_are_silent(self):
        corpus = [
            _doc("EARS-01", "EARS", "- EARS.01.03.aaaa: a req."),
            _doc("BDD-01", "BDD", "@ears: EARS.01.03.aaaa\nScenario."),
            _doc("SPEC-01", "SPEC", "a spec"),
            _doc("TDD-01", "TDD", "@spec: SPEC-01\n- TDD.01.04.aaaa: a test."),
        ]
        self.assertEqual(_check_ref_granularity(corpus), [])


class TagSyntaxPage(unittest.TestCase):
    def test_tag_syntax_page_present_and_draws_the_boundary(self):
        # CLEANUP-001: single framework copy — the vendored platform mirror is gone.
        page = (FRAMEWORK / "governance" / "TAG_SYNTAX.md").read_text(encoding="utf-8")
        self.assertIn("REFGRAN01", page)
        # cross-refs the granularity authority (GD-03 / ID_NAMING), not duplicates
        self.assertIn("ID_NAMING_STANDARDS.md", page)
        self.assertIn("GD-03", page)
        # the carve-outs (self-tags + downstream pointers) are documented
        self.assertIn("Self-tag", page)

    def test_chg_provenance_tag_is_defined_and_the_auditor_can_cite_it(self):
        """`@chg: CHG-NN` has a definition, and C1's citation resolves (GD-11).

        #448 was exactly this defect in the other direction: the CHG auditor's
        C1 made the tag a **P1** requirement while the tag was defined on no spec
        surface. The definition is the only additive-normative item in the
        `0.41.0` release and so the only reason it is MINOR — and it shipped with
        no guard, which is the drift that produced #448. Both halves are pinned
        here: delete the section, or let C1's cross-reference go stale, and this
        fails.
        """
        # CLEANUP-001: single framework copy — the vendored platform mirror is gone.
        page = (FRAMEWORK / "governance" / "TAG_SYNTAX.md").read_text(encoding="utf-8")
        auditor = (FRAMEWORK / "playbooks" / "09_CHG" / "auditor.md").read_text(encoding="utf-8")
        self.assertIn("@chg: CHG-NN", page)
        # non-trace is the load-bearing half: CHG is a governance overlay,
        # not one of the 8 registry layers, so it carries no lineage.
        self.assertIn("**not a trace tag**", page)
        # placement must stay a single decidable rule — a P1 check cites it
        self.assertIn("One rule,", page)
        # and the auditor must still point at this page
        self.assertIn("TAG_SYNTAX", auditor)


class SPEC00CoverageSection(unittest.TestCase):
    def test_coverage_section_and_necessary_upstream_present(self):
        # CLEANUP-001: single framework copy — the vendored platform mirror is gone.
        tpl = (FRAMEWORK / "layers" / "06_SPEC" / "SPEC-00_index.TEMPLATE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## Coverage", tpl)
        self.assertIn("COV02", tpl)
        self.assertIn("**Upstream (necessary)**: EARS, BDD, ADR", tpl)
        # the stale cumulative form is gone from the necessary-upstream line
        self.assertNotIn("**Upstream**: BRD, PRD, EARS, BDD, ADR", tpl)


class BRDTemplateRule(unittest.TestCase):
    def test_authored_fr_annotation_rule_present(self):
        # CLEANUP-001: single framework copy — the vendored platform mirror is gone.
        tpl = (FRAMEWORK / "layers" / "01_BRD" / "BRD-TEMPLATE.yaml").read_text(encoding="utf-8")
        self.assertIn("_authored_form", tpl)
        self.assertIn("Acceptance criteria:", tpl)
        self.assertIn("(P1|P2|Future", tpl)
        self.assertIn("realized_by", tpl)


class PhaseLeakContract(unittest.TestCase):
    """COV03 (D54-F13 / D-0055) — a deferred (``Future``-banded) FR that IS
    realized downstream draws an advisory; the inverse of COV01's escape."""

    _FR = "## 7. Functional Requirements\n\n- **BRD.01.07.aaaa — F** ({band}): a thing."

    def _brd(self, band):
        return _doc("BRD-01", "BRD", self._FR.format(band=band))

    _PRD = _doc("PRD-01", "PRD", "@brd: BRD.01.07.aaaa")
    _PRD_NOCITE = _doc("PRD-01", "PRD", "no citation here")

    def test_deferred_fr_realized_downstream_warns(self):
        findings = _check_phase_leak([self._brd("Future"), self._PRD])
        self.assertEqual([(f.code, f.severity) for f in findings], [("COV03", "warning")])
        self.assertIn("phase-leak", findings[0].message)

    def test_deferred_fr_not_realized_is_silent(self):
        self.assertEqual(_check_phase_leak([self._brd("Future"), self._PRD_NOCITE]), [])

    def test_authored_fr_is_not_cov03(self):
        # A P1 (AUTHORED) FR is COV01's domain, never COV03.
        self.assertEqual(_check_phase_leak([self._brd("P1"), self._PRD]), [])

    def test_realized_by_fr_is_not_cov03(self):
        # `realized_by:` → REALIZED_BY (a positive coverage claim), never DEFERRED.
        self.assertEqual(_check_phase_leak([self._brd("Future, realized_by: ADR"), self._PRD]), [])

    def test_advisory_in_both_modes(self):
        # Never escalates to error, unlike COV01.
        for mode in ("build", "gate-code"):
            findings = _check_phase_leak([self._brd("Future"), self._PRD], mode=mode)
            self.assertEqual([f.severity for f in findings], ["warning"], mode)

    def test_runs_without_spec_or_iplan(self):
        # COV03 must NOT inherit COV01's {SPEC,IPLAN} corpus precondition — it
        # fires on a BRD+PRD-only corpus (the early-stage cascade).
        findings = _check_phase_leak([self._brd("Future"), self._PRD])
        self.assertEqual([f.code for f in findings], ["COV03"])


if __name__ == "__main__":
    unittest.main()
