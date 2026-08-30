"""Conformance: at least one acceptance target actually exercises ``COV01``.

`COV01` is the framework's **forward-coverage** gate — every in-scope BRD
functional requirement must reach a SPEC and an IPLAN, an error in ``gate-code``.
A gate that grades zero requirements passes silently and forever, and that is
indistinguishable from a gate that passes because the corpus is correct.

**Regression cover: #577.** Every acceptance fixture authored its §7 as
``### <ID> <Title>`` level-3 headings. `scan_fr_elements` requires the bullet
form `BRD-TEMPLATE.yaml` `functional_requirements._authored_form` prescribes
normatively — ``- **<ID> — <Title>** (<band>): …`` — so **not one fixture yielded
a single functional requirement**, `COV01` fired on no target, and no manifest
pinned one. The scanner was right; the fixtures were not.

**This asserts liveness, not silence.** Both halves matter and the second is the
one that was missing: the fixtures must yield FRs *and* an uncovered FR must
actually produce a finding. Asserting only that the corpus is clean is what let
the blind state persist — a blind gate and a satisfied gate are both quiet.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from _spec import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import lint_path, scan_fr_elements  # noqa: E402

FIXTURES = REPO_ROOT / "tests" / "acceptance" / "fixtures"

# The one target with a complete BRD→…→IPLAN graph, and therefore the only place
# forward coverage is meaningful. The per-layer targets stage upstreams as
# context and their `.yaml` downstreams carry an unterminated `---` fence, so
# they are invisible to `build_edge_graph` and their BRD never reaches SPEC —
# a separate defect, tracked on #478, with a measured manifest cost.
CHAIN = FIXTURES / "fullpath" / "golden_chain"
CHAIN_BRD = CHAIN / "01_BRD" / "BRD-01_golden.md"


class ForwardCoverageIsExercised(unittest.TestCase):
    def test_the_chain_brd_yields_functional_requirements(self):
        frs = scan_fr_elements(CHAIN_BRD.read_text(encoding="utf-8"))
        self.assertTrue(
            frs,
            f"{CHAIN_BRD.relative_to(REPO_ROOT)} yields no FR to scan_fr_elements — "
            "§7 must use the normative bullet form from BRD-TEMPLATE.yaml "
            "`functional_requirements._authored_form`, or COV01 grades nothing (#577)",
        )

    def test_every_yielded_fr_carries_a_band(self):
        """The band is the machine-readable phase signal.

        Without it an FR classifies as in-scope by default, so the fixture would
        still exercise COV01 — but by accident. `_authored_form` calls the band
        normative; assert it rather than rely on the default.
        """
        for fr in scan_fr_elements(CHAIN_BRD.read_text(encoding="utf-8")):
            with self.subTest(fr=fr.elem_id):
                self.assertIn(fr.band, ("P1", "P2", "Future"), f"{fr.elem_id} has band {fr.band!r}")

    def test_an_uncovered_requirement_actually_produces_cov01(self):
        """Liveness. Injects an FR nothing realizes and asserts COV01 fires.

        Adding an FR rather than renaming an existing one is deliberate: renaming
        makes every downstream ``@brd:`` citation unresolvable, so TRACE-RES-001
        fires first and COV01's absence proves nothing. That faulty probe is how
        this test's first draft concluded the gate was dead on targets where it
        is merely inapplicable.
        """
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "chain"
            shutil.copytree(CHAIN, work)
            brd = work / "01_BRD" / "BRD-01_golden.md"
            text = brd.read_text(encoding="utf-8")
            anchor = "\n\nAcceptance criteria:"
            self.assertIn(anchor, text, "the fixture lost its acceptance-criteria boundary")
            brd.write_text(
                text.replace(
                    anchor,
                    "\n- **BRD.01.07.c0de — Uncovered capability** (P1): "
                    "a requirement nothing downstream picks up." + anchor,
                    1,
                ),
                encoding="utf-8",
            )
            codes = [f.code for f in lint_path(work)]
            self.assertIn(
                "COV01",
                codes,
                "an uncovered in-scope FR produced no COV01 — forward coverage is "
                f"not being evaluated on {CHAIN.relative_to(REPO_ROOT)}. Codes seen: "
                f"{sorted(set(codes))}",
            )

    def test_the_unmodified_chain_is_cov01_clean(self):
        """The control: quiet because satisfied, which the test above distinguishes."""
        codes = [f.code for f in lint_path(CHAIN)]
        self.assertNotIn("COV01", codes, "the golden chain should satisfy forward coverage")


if __name__ == "__main__":
    unittest.main()
