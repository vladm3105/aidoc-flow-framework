"""Conformance: GD-14's 5-FR-per-BRD cap is measured, and stays ADVISORY.

GD-14 makes it normative that a BRD document **SHOULD** carry at most five
functional requirements. #540 records that nothing measured it: a 12-requirement
BRD passed `sdd_doc_lint`, the conformance suite and the BRD auditor lens. The
rule was guidance a human reviewer applied, on a layer usually authored by an LLM
reading `_guidance` blocks.

`FRCAP01` closes the measurement gap **without** converting the SHOULD into a
gate — which is the part this module exists to lock. #540's own framing is that
the cap was *requested* as guidance rather than as a gate, so an escalation here
would silently overrule a deliberate scope decision.

**This ships with its own fixture because #540 could not otherwise be tested.**
Measured before writing it: of every BRD in the repository, the example corpus's
carried 4 visible FRs and no acceptance fixture yielded any at all. There was no
document anywhere that a cap check would fire on, so a check landing without a
fixture would have been born untestable and green.
"""

from __future__ import annotations

import sys
import unittest

from _spec import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import FR_CAP, _check_fr_cap, lint_path, scan_fr_elements  # noqa: E402

FIXTURE = REPO_ROOT / "tests" / "acceptance" / "fixtures" / "negative" / "brd-fr-cap-exceeded.md"


class FrCapIsMeasured(unittest.TestCase):
    def test_the_cap_is_five(self):
        """GD-14's number, pinned. Changing it is a spec change, not a tweak."""
        self.assertEqual(FR_CAP, 5)

    def test_the_fixture_exceeds_the_cap(self):
        """Guards the guard — a fixture that stopped exceeding proves nothing below."""
        frs = scan_fr_elements(FIXTURE.read_text(encoding="utf-8"))
        self.assertGreater(len(frs), FR_CAP, "the negative fixture no longer exceeds the cap")
        self.assertEqual(len(frs), 7, "fixture FR count changed — update this expectation")

    def test_acceptance_criteria_do_not_count(self):
        """The `Acceptance criteria:` boundary is load-bearing for the count.

        GD-14's counting rule was written against the same boundary ``COV01``
        uses, so the cap counts what the coverage gate counts. The fixture
        carries three IDs after that line; counting them would report 10.
        """
        text = FIXTURE.read_text(encoding="utf-8")
        ids = [f.elem_id for f in scan_fr_elements(text)]
        self.assertNotIn("BRD.91.07.b001", ids, "an acceptance criterion was counted as an FR")
        self.assertTrue(all(i.startswith("BRD.91.07.a") for i in ids))

    def test_escaped_requirements_still_count(self):
        """Deliberate: the two coverage exemptions do not transfer to the cap.

        A ``Future``-banded or ``realized_by:``-tagged FR escapes ``COV01``
        because it carries no coverage obligation. It is still a requirement the
        document carries, and the cap is about document **size**. Asserted so a
        future reader does not "fix" the count by reusing ``covered_state_of``.
        """
        frs = scan_fr_elements(FIXTURE.read_text(encoding="utf-8"))
        self.assertIn("Future", [f.band for f in frs])
        self.assertIn("ADR", [f.realized_by for f in frs])
        self.assertEqual(len(frs), 7)

    def test_it_fires_and_is_advisory(self):
        findings = _check_fr_cap([("brd-fr-cap-exceeded.md", FIXTURE.read_text(encoding="utf-8"))])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, "FRCAP01")
        self.assertEqual(
            findings[0].severity,
            "warning",
            "FRCAP01 must stay advisory — GD-14 states the cap as a SHOULD and #540 records "
            "that it was requested as guidance rather than as a gate",
        )

    def test_it_never_escalates_in_gate_code(self):
        """The escalation guard. This is the assertion that keeps the SHOULD a SHOULD.

        ``COV01`` and ``REFGRAN01`` both escalate warning→error in ``gate-code``;
        a contributor adding FRCAP01 to that pattern would convert a deliberate
        guidance rule into a merge blocker without a spec change.
        """
        for mode in ("build", "gate-code"):
            with self.subTest(mode=mode):
                findings = [f for f in lint_path(FIXTURE, mode=mode) if f.code == "FRCAP01"]
                self.assertEqual(len(findings), 1, f"FRCAP01 did not fire in {mode}")
                self.assertEqual(findings[0].severity, "warning", f"FRCAP01 escalated in {mode}")

    def test_a_conformant_brd_is_silent(self):
        """The control: the example corpus is at 4 of 5 and must not warn."""
        corpus = REPO_ROOT / "examples" / "url-shortener" / "docs"
        self.assertFalse([f for f in lint_path(corpus) if f.code == "FRCAP01"])


if __name__ == "__main__":
    unittest.main()
