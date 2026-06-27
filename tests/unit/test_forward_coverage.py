"""Unit: the forward coverage gate (CFB-PR-2 2a-core step 4, DD-6 rows 2-3 + DD-1/DD-9).

Every in-scope (AUTHORED) BRD functional requirement must reach >=1 SPEC and
>=1 IPLAN downstream (document-level binding from the FR's host BRD — PR-3
refines to element-level). Escaped FRs (deferred / realized_by) never block.
Run-mode severity: no-SPEC blocks in both modes; SPEC-but-no-IPLAN warns in
`build` and blocks in `gate-code`. The check is gated to whole-corpus runs that
have reached the SPEC and IPLAN layers (DD-1) — it no-ops otherwise (incl. the
single-file on_author case).
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root  # noqa: E402

sys.path.insert(0, str(plugin_bundle_root()))
from sdd_doc_lint import _check_forward_coverage, lint_path  # noqa: E402

_ORDER = ["BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN"]


def _doc(doc_id: str, artifact_type: str, body: str) -> tuple[str, str]:
    text = f"---\ndoc_id: {doc_id}\nartifact_type: {artifact_type}\n---\n\n{body}\n"
    return (f"{doc_id}.md", text)


def _brd(band="P1", realized_by=None, elem="BRD.01.07.aaaa") -> tuple[str, str]:
    ann = f"({band}" + (f", realized_by: {realized_by}" if realized_by else "") + ")"
    body = f"## 7. Functional Requirements\n\n- **{elem} — Feature** {ann}: do a thing."
    return _doc("BRD-01", "BRD", body)


def _chain(last_layer: str, **brd_kw) -> list[tuple[str, str]]:
    """A connected cascade BRD..last_layer; each downstream cites its immediate
    upstream's doc id. BRD-01 carries one FR (configurable band/escape)."""
    upto = _ORDER[: _ORDER.index(last_layer) + 1]
    corpus = [_brd(**brd_kw)]
    for i in range(1, len(upto)):
        layer, up = upto[i], upto[i - 1]
        corpus.append(_doc(f"{layer}-01", layer, f"Realises @{up.lower()}: {up}-01 here."))
    return corpus


def _codes(findings):
    return [(f.code, f.severity, f.message) for f in findings]


class GateRunsOnlyOnFullCascade(unittest.TestCase):
    def test_no_spec_in_corpus_is_noop(self):
        self.assertEqual(_check_forward_coverage(_chain("EARS")), [])

    def test_no_iplan_in_corpus_is_noop(self):
        # chain reaches SPEC but the corpus has no IPLAN doc at all.
        self.assertEqual(_check_forward_coverage(_chain("SPEC")), [])

    def test_single_brd_file_is_noop(self):
        self.assertEqual(_check_forward_coverage([_brd()]), [])


class AuthoredCoverage(unittest.TestCase):
    def test_fully_covered_fr_has_no_finding(self):
        self.assertEqual(_check_forward_coverage(_chain("IPLAN")), [])

    def test_no_spec_reach_blocks_in_both_modes(self):
        # BRD reaches nothing; SPEC + IPLAN exist but disconnected → gate runs.
        corpus = [
            _brd(),
            _doc("SPEC-99", "SPEC", "Standalone spec, cites nothing relevant."),
            _doc("IPLAN-99", "IPLAN", "Standalone iplan, cites nothing relevant."),
        ]
        for mode in ("build", "gate-code"):
            findings = _check_forward_coverage(corpus, mode)
            self.assertEqual(len(findings), 1, mode)
            self.assertEqual(findings[0].code, "COV01")
            self.assertEqual(findings[0].severity, "error", mode)
            self.assertIn("no SPEC", findings[0].message)

    def test_spec_but_no_iplan_warns_in_build_blocks_in_gate_code(self):
        # Chain reaches SPEC; a disconnected IPLAN exists so the gate runs but the
        # FR's host BRD does not reach it.
        corpus = _chain("SPEC") + [
            _doc("IPLAN-99", "IPLAN", "Standalone iplan, disconnected from the chain.")
        ]
        build = _check_forward_coverage(corpus, "build")
        self.assertEqual([(f.code, f.severity) for f in build], [("COV01", "warning")])
        self.assertIn("no IPLAN", build[0].message)
        gate = _check_forward_coverage(corpus, "gate-code")
        self.assertEqual([(f.code, f.severity) for f in gate], [("COV01", "error")])


class EscapesNeverBlock(unittest.TestCase):
    def _uncovered_corpus(self, **brd_kw):
        return [
            _brd(**brd_kw),
            _doc("SPEC-99", "SPEC", "Standalone spec."),
            _doc("IPLAN-99", "IPLAN", "Standalone iplan."),
        ]

    def test_deferred_future_fr_does_not_block(self):
        self.assertEqual(_check_forward_coverage(self._uncovered_corpus(band="Future")), [])

    def test_realized_by_fr_does_not_block(self):
        self.assertEqual(
            _check_forward_coverage(self._uncovered_corpus(band="P1", realized_by="ADR")), []
        )


class LintPathWiring(unittest.TestCase):
    """Integration: the gate is wired into lint_path on a directory run, honours
    --mode, and is suppressed by skip_coverage."""

    def _write(self, td: Path, corpus):
        for rel, text in corpus:
            (td / rel).write_text(text, encoding="utf-8")

    def _cov(self, findings):
        return [f for f in findings if f.code == "COV01"]

    def test_mode_and_skip_through_lint_path(self):
        corpus = _chain("SPEC") + [_doc("IPLAN-99", "IPLAN", "Disconnected iplan.")]
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            self._write(tdp, corpus)
            build = self._cov(lint_path(tdp, mode="build"))
            self.assertEqual([f.severity for f in build], ["warning"])
            gate = self._cov(lint_path(tdp, mode="gate-code"))
            self.assertEqual([f.severity for f in gate], ["error"])
            skipped = self._cov(lint_path(tdp, mode="gate-code", skip_coverage=True))
            self.assertEqual(skipped, [])


if __name__ == "__main__":
    unittest.main()
