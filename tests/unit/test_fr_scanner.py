"""Unit: the heading-context FR scanner (CFB-PR-2 DD-3).

Locks in the forward-coverage engine's notion of a *gated* functional
requirement: an element id authored as an FR definition bullet under a
``## … Functional Requirements`` heading and BEFORE that section's
``Acceptance criteria:`` label line. Prose citations of element ids inside the
section, and the §7 acceptance-criteria sub-block elements, are NOT gated.

Modelled on the real ``examples/url-shortener/docs/01_BRD/BRD-01.md`` §7 shape
(R-b): FR bullets ``- **ID — Title** (P1, …)`` followed by a plain
``Acceptance criteria:`` prose label and AC bullets under the same ``.07.``
ordinal.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root  # noqa: E402

sys.path.insert(0, str(plugin_bundle_root()))
from sdd_doc_lint import scan_fr_elements  # noqa: E402

# A faithful miniature of the corpus §7 shape — FR bullets, an intervening
# prose paragraph that *cites* FR + AC element ids, the `Acceptance criteria:`
# boundary, then AC bullets, then the next `##` section.
BRD_BODY = """\
## 6. Stakeholders

| Role | Concern |
| ---- | ------- |
| Owner | wants it to work |

## 7. Functional Requirements

Access classes are fixed at this layer.

- **BRD.01.07.6c3f — Submit and Shorten URL** (P1, anonymous public): The service
  SHALL accept a well-formed URL and return a short code.
- **BRD.01.07.15e1 — Redirect Short Link** (P1, anonymous public): The service
  SHALL redirect a request for a short code to its original URL.
- **BRD.01.07.882c — Count Visits** (P2, internal / privileged — Service-Owner
  role): The service SHALL count visits and surface the count to the Owner.

Shared-data ownership: the Submit path (BRD.01.07.6c3f) owns creation; the
Resolve path (BRD.01.07.15e1 read, BRD.01.07.390f increment) owns reads.

Acceptance criteria:

- **BRD.01.07.d088 — Redirect Resolves**: Given a code, when requested, then
  the service redirects to the original URL.
- **BRD.01.07.390f — Visit Count Accurate**: Each visit increases the count by
  one, accurate under concurrency.

## 8. ADR Topics

- **BRD.01.08.aaaa — Some Topic** (P1, n/a): not a functional requirement.
"""


class ScanFRElements(unittest.TestCase):
    def setUp(self):
        self.frs = scan_fr_elements(BRD_BODY)
        self.ids = [fr.elem_id for fr in self.frs]

    def test_gated_frs_are_the_three_definition_bullets(self):
        self.assertEqual(
            self.ids,
            ["BRD.01.07.6c3f", "BRD.01.07.15e1", "BRD.01.07.882c"],
        )

    def test_acceptance_criteria_block_is_not_gated(self):
        # d088 / 390f are defined after the `Acceptance criteria:` boundary.
        self.assertNotIn("BRD.01.07.d088", self.ids)
        self.assertNotIn("BRD.01.07.390f", self.ids)

    def test_prose_citations_are_not_gated(self):
        # 390f is *cited* in the §7 ownership paragraph (before the boundary) but
        # only *defined* in the AC block — a citation must never make it gated.
        cite_lines = [fr for fr in self.frs if fr.elem_id == "BRD.01.07.390f"]
        self.assertEqual(cite_lines, [])

    def test_elements_outside_fr_section_are_not_gated(self):
        # The §8 bullet has the FR-bullet form + a band, but lives under a
        # different `##` heading — not gated.
        self.assertNotIn("BRD.01.08.aaaa", self.ids)

    def test_band_token_is_captured(self):
        by_id = {fr.elem_id: fr.band for fr in self.frs}
        self.assertEqual(by_id["BRD.01.07.6c3f"], "P1")
        # 882c's parenthetical wraps to the next line; the leading token still
        # parses from the bullet's first line.
        self.assertEqual(by_id["BRD.01.07.882c"], "P2")

    def test_band_is_none_when_bullet_has_no_parenthetical(self):
        body = (
            "## 7. Functional Requirements\n\n"
            "- **BRD.01.07.abcd — No Band Here** The service SHALL do a thing.\n"
        )
        frs = scan_fr_elements(body)
        self.assertEqual([(f.elem_id, f.band) for f in frs], [("BRD.01.07.abcd", None)])

    def test_line_numbers_point_at_the_bullet(self):
        first = next(fr for fr in self.frs if fr.elem_id == "BRD.01.07.6c3f")
        self.assertEqual(BRD_BODY.splitlines()[first.line - 1].lstrip()[:6], "- **BR")


class ScanFREmptyAndEdge(unittest.TestCase):
    def test_no_fr_section_returns_empty(self):
        self.assertEqual(scan_fr_elements("## 1. Intro\n\nNo requirements here.\n"), [])

    def test_fr_section_with_no_bullets_returns_empty(self):
        body = "## 7. Functional Requirements\n\nNarrative only, no bullets.\n"
        self.assertEqual(scan_fr_elements(body), [])


if __name__ == "__main__":
    unittest.main()
