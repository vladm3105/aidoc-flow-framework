"""Unit: tools/sdd_coverage.py — the forward-coverage traceability matrix
emitter (CFB-PR-2 2a-core step 5, DD-7).

A thin reporter over the shared `build_edge_graph` core: for each gated BRD
functional requirement it renders the band, covered_state, and the downstream
layers its host BRD transitively reaches (document-level binding; PR-3 refines
to element granularity). The output is GENERATED + deterministic — the
conformance gate regenerates and diffs it (V5).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from sdd_coverage import render_matrix  # noqa: E402

_ORDER = ["BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN"]


def _doc(doc_id: str, artifact_type: str, body: str) -> tuple[str, str]:
    return (
        f"{doc_id}.md",
        f"---\ndoc_id: {doc_id}\nartifact_type: {artifact_type}\n---\n\n{body}\n",
    )


def _brd(elem="BRD.01.07.aaaa", band="P1") -> tuple[str, str]:
    body = f"## 7. Functional Requirements\n\n- **{elem} — Feature** ({band}): a thing."
    return _doc("BRD-01", "BRD", body)


def _chain(last_layer: str) -> list[tuple[str, str]]:
    upto = _ORDER[: _ORDER.index(last_layer) + 1]
    corpus = [_brd()]
    for i in range(1, len(upto)):
        layer, up = upto[i], upto[i - 1]
        corpus.append(_doc(f"{layer}-01", layer, f"Realises @{up.lower()}: {up}-01 here."))
    return corpus


class RenderMatrix(unittest.TestCase):
    def test_fully_covered_fr_row_has_all_checks(self):
        out = render_matrix(_chain("IPLAN"))
        self.assertIn("BRD.01.07.aaaa", out)
        # the FR row should mark every downstream layer reached.
        row = next(ln for ln in out.splitlines() if "BRD.01.07.aaaa" in ln)
        self.assertEqual(row.count("✓"), 7)  # PRD..IPLAN
        self.assertIn("authored", row)
        self.assertIn("P1", row)

    def test_partial_reach_shows_missing_layers(self):
        out = render_matrix(_chain("SPEC"))  # reaches PRD..SPEC, not TDD/IPLAN
        row = next(ln for ln in out.splitlines() if "BRD.01.07.aaaa" in ln)
        self.assertEqual(row.count("✓"), 5)  # PRD,EARS,BDD,ADR,SPEC

    def test_deferred_fr_state_rendered(self):
        out = render_matrix([_brd(band="Future")] + _chain("IPLAN")[1:])
        row = next(ln for ln in out.splitlines() if "BRD.01.07.aaaa" in ln)
        self.assertIn("deferred", row)

    def test_deterministic_and_sorted(self):
        corpus = _chain("IPLAN") + [
            _doc(
                "BRD-02",
                "BRD",
                "## 7. Functional Requirements\n\n- **BRD.02.07.fff0 — Z** (P2): z.",
            ),
        ]
        out1 = render_matrix(corpus)
        out2 = render_matrix(list(reversed(corpus)))  # input order must not matter
        self.assertEqual(out1, out2)
        # rows sorted by FR id → aaaa before fff0
        self.assertLess(out1.index("BRD.01.07.aaaa"), out1.index("BRD.02.07.fff0"))

    def test_generated_banner_and_no_hand_edit_warning(self):
        out = render_matrix(_chain("IPLAN"))
        self.assertIn("GENERATED", out)
        self.assertIn("sdd_coverage.py", out)

    def test_empty_corpus_renders_no_requirements_note(self):
        out = render_matrix([_doc("PRD-01", "PRD", "no requirements here")])
        self.assertIn("no functional requirements", out.lower())

    def test_brd_identification_matches_the_gate_classifier(self):
        # A doc whose id merely starts with "BRD" (BRDX-01) is NOT a BRD — the
        # matrix must agree with the gate's _artifact_code classifier and skip
        # it, never list its FR row.
        corpus = _chain("IPLAN") + [
            _doc(
                "BRDX-01",
                "",  # no artifact_type → _artifact_code falls back to the prefix
                "## 7. Functional Requirements\n\n- **BRDX.01.07.abcd — X** (P1): x.",
            ),
        ]
        out = render_matrix(corpus)
        self.assertNotIn("BRDX.01.07.abcd", out)
        self.assertIn("BRD.01.07.aaaa", out)  # the genuine BRD still listed

    def test_band_with_pipe_is_escaped(self):
        out = render_matrix([_brd(band="P1|x")] + _chain("IPLAN")[1:])
        row = next(ln for ln in out.splitlines() if "BRD.01.07.aaaa" in ln)
        self.assertIn("P1\\|x", row)  # escaped, table not corrupted


if __name__ == "__main__":
    unittest.main()
