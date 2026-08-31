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
from sdd_doc_lint import (  # noqa: E402
    FR_CAP,
    _check_fr_cap,
    _fr_elements,
    lint_path,
    scan_fr_elements,
)

FIXTURE = REPO_ROOT / "tests" / "acceptance" / "fixtures" / "negative" / "brd-fr-cap-exceeded.md"


#: A BRD authored as `BRD-TEMPLATE.yaml` prescribes -- the carrier GD-15 makes
#: mandatory. Built inline rather than committed: the point is the carrier, and a
#: second on-disk fixture would need its own manifest registration.
#:
#: The keys are the TEMPLATE's, not invented ones: `BRD-TEMPLATE.yaml`
#: `functional_requirements.requirements[]` declares `id` / `title` / `capability`
#: / `priority` / `realized_by`, and `scan_fr_elements_yaml` maps `priority` onto
#: `FRElement.band`. An earlier draft used `text:` and `band:` -- neither of which
#: exists -- so every row came back `band=None`. The count tests still passed
#: (only `id` is needed for a count), so the fixture could not have caught a
#: regression in that mapping while looking like it did. Caught on OPS-0065
#: review; `test_the_yaml_fixture_uses_the_template_key_names` is the lock.
_YAML_BRD_OVER_CAP = (
    "doc_id: BRD-01\nartifact_type: BRD\nfunctional_requirements:\n  requirements:\n"
    + "".join(
        f"    - id: BRD.01.07.{i:04d}\n      title: requirement {i}\n      priority: P1\n"
        for i in range(1, FR_CAP + 3)
    )
)


class FrCapIsCarrierAware(unittest.TestCase):
    """Regression lock for the seam this rule shipped without.

    `_check_fr_cap` originally read `_extract_frontmatter(text)` with no `rel`
    and then `scan_fr_elements` -- the Markdown scanner -- so on a `.yaml` BRD
    `_artifact_code` returned '' and the document was skipped before it was ever
    counted. The cap was dead on the format the spec mandates, while its own
    docstring claimed it "counts exactly what COV01 grades" and COV01 dispatches
    through `_fr_elements`. Caught by OPS-0065 review of the 0.47.0 combine.

    Asserts the CLASSIFICATION on both carriers, not just a finding count: a
    count alone passes for the wrong reason if the document stops being seen as
    a BRD at all -- which is exactly how the original defect hid.
    """

    def test_the_yaml_fixture_is_over_cap_and_seen_as_a_brd(self):
        """Guards the guard: if either is false every assertion below is vacuous."""
        from sdd_doc_lint import _artifact_code, _extract_frontmatter

        fm = _extract_frontmatter(_YAML_BRD_OVER_CAP, "BRD-01.yaml")
        self.assertEqual("BRD", _artifact_code(fm))
        self.assertGreater(len(_fr_elements(_YAML_BRD_OVER_CAP, "BRD-01.yaml", fm)), FR_CAP)

    def test_the_yaml_fixture_uses_the_template_key_names(self):
        """The fixture must have the shape a real YAML BRD has, not a plausible one.

        `scan_fr_elements_yaml` reads `priority` for the band. A fixture using an
        invented key still yields the right element COUNT -- only `id` is needed
        for that -- so the firing test below passes either way. This asserts the
        mapping actually resolved, which is what makes the fixture evidence about
        the real carrier rather than about itself.
        """
        from sdd_doc_lint import _extract_frontmatter

        fm = _extract_frontmatter(_YAML_BRD_OVER_CAP, "BRD-01.yaml")
        bands = [fr.band for fr in _fr_elements(_YAML_BRD_OVER_CAP, "BRD-01.yaml", fm)]
        self.assertTrue(
            bands and all(b == "P1" for b in bands),
            "the fixture's `priority:` did not reach `FRElement.band` -- it is using a key "
            f"`BRD-TEMPLATE.yaml` does not define; got {bands}",
        )

    def test_frcap01_fires_on_a_yaml_brd(self):
        found = [
            f for f in _check_fr_cap([("BRD-01.yaml", _YAML_BRD_OVER_CAP)]) if f.code == "FRCAP01"
        ]
        self.assertEqual(
            1,
            len(found),
            "FRCAP01 did not fire on a YAML BRD over the cap -- the rule is "
            "Markdown-only again; re-check `_check_fr_cap`'s use of `_fr_elements`",
        )

    def test_frcap01_stays_a_warning_on_the_yaml_carrier_too(self):
        found = [
            f for f in _check_fr_cap([("BRD-01.yaml", _YAML_BRD_OVER_CAP)]) if f.code == "FRCAP01"
        ]
        self.assertEqual(["warning"], [f.severity for f in found])

    def test_the_yaml_finding_carries_a_one_based_line(self):
        """`scan_fr_elements_yaml` sets `line=0` for every element, by design.

        Publishing that straight through as a `Finding.line` hands a 1-based
        consumer -- an editor annotation, an acceptance-manifest matcher -- an
        out-of-range value. `_check_fr_cap` falls back to the doc-level `1`, as
        `PROV01` does. Measured on OPS-0065 round 4: reverting that `or 1`
        SURVIVED the whole 454-test tier, because nothing asserted the line.
        """
        found = [
            f for f in _check_fr_cap([("BRD-01.yaml", _YAML_BRD_OVER_CAP)]) if f.code == "FRCAP01"
        ]
        self.assertEqual(
            [1],
            [f.line for f in found],
            "FRCAP01 published a 0 line on the YAML carrier; findings are 1-based",
        )


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
