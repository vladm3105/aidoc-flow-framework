"""Unit: the covered_state enum + band parser + escape classifier (CFB-PR-2
DD-2 / DD-4 / DD-5).

`parse_band` validates the FR-bullet band token against the priority bands
single-sourced in `priority_definitions` (BRD-TEMPLATE.yaml). `covered_state_of`
classifies a gated FR into a `CoveredState`: the success state `authored` (must
reach downstream), or a non-blocking escape (`deferred` for a `Future` band,
`realized_by` for a layer-realised FR). `satisfied_by_reference` is an enum
member only (PR-5 adds its logic — never produced here).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root  # noqa: E402

sys.path.insert(0, str(plugin_bundle_root()))
from sdd_doc_lint import (  # noqa: E402
    CoveredState,
    FRElement,
    covered_state_of,
    parse_band,
    scan_fr_elements,
)


class ParseBand(unittest.TestCase):
    def test_canonical_bands_passthrough(self):
        self.assertEqual(parse_band("P1"), "P1")
        self.assertEqual(parse_band("P2"), "P2")
        self.assertEqual(parse_band("Future"), "Future")

    def test_case_insensitive(self):
        self.assertEqual(parse_band("p1"), "P1")
        self.assertEqual(parse_band("future"), "Future")

    def test_unknown_or_missing_is_none(self):
        for tok in (None, "", "P3", "P0", "later", "garbage"):
            self.assertIsNone(parse_band(tok), tok)


class CoveredStateOf(unittest.TestCase):
    def _fr(self, band=None, realized_by=None):
        return FRElement(elem_id="BRD.01.07.aaaa", line=1, band=band, realized_by=realized_by)

    def test_in_scope_band_is_authored(self):
        self.assertEqual(covered_state_of(self._fr(band="P1")), CoveredState.AUTHORED)
        self.assertEqual(covered_state_of(self._fr(band="P2")), CoveredState.AUTHORED)

    def test_future_band_is_deferred(self):
        self.assertEqual(covered_state_of(self._fr(band="Future")), CoveredState.DEFERRED)

    def test_missing_or_invalid_band_is_authored(self):
        # A missing/invalid band classifies as authored (the gate requires reach
        # and reports the missing-band finding separately) — never silently an
        # escape.
        self.assertEqual(covered_state_of(self._fr(band=None)), CoveredState.AUTHORED)
        self.assertEqual(covered_state_of(self._fr(band="P3")), CoveredState.AUTHORED)

    def test_realized_by_is_an_escape(self):
        self.assertEqual(covered_state_of(self._fr(realized_by="ADR")), CoveredState.REALIZED_BY)

    def test_realized_by_takes_precedence_over_band(self):
        # An explicit realized_by claim wins over the band (both are escapes; the
        # state label reflects the more specific positive claim).
        self.assertEqual(
            covered_state_of(self._fr(band="Future", realized_by="ADR")),
            CoveredState.REALIZED_BY,
        )

    def test_satisfied_by_reference_is_never_produced(self):
        # The enum member exists (PR-5 extension point) but no input yields it.
        self.assertIn("satisfied_by_reference", [s.value for s in CoveredState])
        produced = {
            covered_state_of(self._fr(band=b, realized_by=r))
            for b in (None, "P1", "P2", "Future", "P3")
            for r in (None, "ADR")
        }
        self.assertNotIn(CoveredState.SATISFIED_BY_REFERENCE, produced)


class ScannerCapturesRealizedBy(unittest.TestCase):
    def test_realized_by_token_in_parenthetical(self):
        body = (
            "## 7. Functional Requirements\n\n"
            "- **BRD.01.07.aaaa — Audit Trail** (P1, realized_by: ADR): a decision-"
            "only requirement with no dedicated SPEC.\n"
        )
        (fr,) = scan_fr_elements(body)
        self.assertEqual(fr.band, "P1")
        self.assertEqual(fr.realized_by, "ADR")
        self.assertEqual(covered_state_of(fr), CoveredState.REALIZED_BY)

    def test_realized_by_is_none_when_absent(self):
        body = (
            "## 7. Functional Requirements\n\n"
            "- **BRD.01.07.aaaa — Submit** (P1, anonymous public): a normal FR.\n"
        )
        (fr,) = scan_fr_elements(body)
        self.assertIsNone(fr.realized_by)
        self.assertEqual(covered_state_of(fr), CoveredState.AUTHORED)


if __name__ == "__main__":
    unittest.main()
