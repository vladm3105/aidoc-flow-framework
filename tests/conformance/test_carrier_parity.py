"""Conformance: the same content yields the same verdict on either carrier.

**This is the artifact GD-17 requires.** Its effective condition is evaluated by
"a per-layer carrier-parity assertion in the conformance or acceptance tier …
comparing a YAML reference instance against its Markdown counterpart rule by
rule". Until this module existed the condition had no evaluator, so no surface
could honestly say whether it was met.

Scope, stated plainly: this asserts parity for the primitives GD-20 makes
carrier-aware — document identity, structural sections, and the functional-
requirement set with its coverage classification. It does **not** yet assert
parity for every rule in the catalogue, so it does not by itself establish that
GD-17's condition is met. `plans/GD15-CARRIER-CENSUS.md` lists the seams that
remain (`FM01`, which reaches `_split_frontmatter` directly, and
`scan_fr_content` behind `rehash_check`).

The failure this guards against is subtle and one-directional: a carrier-aware
rule that reads *something* on both carriers but not the *same* thing passes
every smoke test and silently grades two documents differently.
"""

from __future__ import annotations

import sys
import unittest

from _spec import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import (  # noqa: E402
    _check_required_template_sections,
    _extract_frontmatter,
    _fr_elements,
    covered_state_of,
    find_registry,
)

# One requirement of each coverage class, so parity is asserted across the whole
# classification rather than on the happy path only.
MD = """---
doc_id: BRD-01
artifact_type: BRD
---

# BRD-01

## 7. Functional Requirements

- **BRD.01.07.a7f3 — Ordinary requirement** (P1): an ordinary capability.
- **BRD.01.07.b1c2 — Deferred requirement** (Future): deferred to a later cycle.
- **BRD.01.07.c3d4 — ADR-realized requirement** (P1, realized_by: ADR): realized off the SPEC path.

Acceptance criteria:

- **BRD.01.07.d5e6 — A criterion**: not a requirement, and must not be counted.

## Traceability

- "@brd: BRD-01"
"""

YAML = """doc_id: BRD-01
artifact_type: BRD
functional_requirements:
  requirements:
    - id: "BRD.01.07.a7f3"
      title: "Ordinary requirement"
      priority: P1
    - id: "BRD.01.07.b1c2"
      title: "Deferred requirement"
      priority: Future
    - id: "BRD.01.07.c3d4"
      title: "ADR-realized requirement"
      priority: P1
      realized_by: ADR
traceability:
  tags:
    - "@brd: BRD-01"
"""


def _fm(text: str, rel: str) -> dict:
    return _extract_frontmatter(text, rel) or {}


class CarrierParity(unittest.TestCase):
    def test_document_identity_matches(self):
        md, ya = _fm(MD, "BRD-01.md"), _fm(YAML, "BRD-01.yaml")
        for key in ("doc_id", "artifact_type"):
            with self.subTest(key=key):
                self.assertEqual(md.get(key), ya.get(key))
                self.assertTrue(md.get(key), f"{key} missing on the Markdown carrier")

    def test_the_fr_sets_are_identical(self):
        md = _fr_elements(MD, "BRD-01.md", _fm(MD, "BRD-01.md"))
        ya = _fr_elements(YAML, "BRD-01.yaml", _fm(YAML, "BRD-01.yaml"))
        self.assertEqual(
            [f.elem_id for f in md],
            [f.elem_id for f in ya],
            "the two carriers disagree on WHICH requirements exist",
        )
        self.assertEqual(len(md), 3, "expected 3 requirements, not the acceptance criterion")

    def test_acceptance_criteria_are_excluded_on_both(self):
        """Excluded positionally on Markdown, structurally on YAML — same result.

        The Markdown carrier bounds the gated set with the literal
        `Acceptance criteria:` line; the structured shape simply uses a different
        key. Different mechanisms, and the assertion is that they agree.
        """
        for text, rel in ((MD, "BRD-01.md"), (YAML, "BRD-01.yaml")):
            with self.subTest(carrier=rel):
                ids = [f.elem_id for f in _fr_elements(text, rel, _fm(text, rel))]
                self.assertNotIn("BRD.01.07.d5e6", ids)

    def test_coverage_classification_matches_per_requirement(self):
        """The parity that matters most — and the one GD-20 was needed for.

        Without `realized_by` in the structured schema every YAML requirement
        classified AUTHORED, so `COV01` became unconditionally blocking on that
        carrier and an ADR-realized requirement had no way to declare itself.
        """
        md = {
            f.elem_id: covered_state_of(f)
            for f in _fr_elements(MD, "BRD-01.md", _fm(MD, "BRD-01.md"))
        }
        ya = {
            f.elem_id: covered_state_of(f)
            for f in _fr_elements(YAML, "BRD-01.yaml", _fm(YAML, "BRD-01.yaml"))
        }
        self.assertEqual(md, ya, "the carriers classify the same requirement differently")
        self.assertEqual(
            {s.name for s in md.values()},
            {"AUTHORED", "DEFERRED", "REALIZED_BY"},
            "the fixture stopped covering all three coverage states",
        )

    def test_struct01_agrees_on_which_sections_are_present(self):
        """A section is a `##` heading or a top-level key — the same unit, named twice."""
        reg = find_registry()
        md = {
            f.section
            for f in _check_required_template_sections("BRD-01.md", MD, "BRD", registry=reg)
        }
        ya = {
            f.section
            for f in _check_required_template_sections("BRD-01.yaml", YAML, "BRD", registry=reg)
        }
        # Guards the guard: an earlier draft passed the arguments in the wrong
        # order, both sides returned zero findings, and the comparison was
        # `set() == set()` — vacuously true. A mutation that broke the YAML
        # section source survived it. Assert the check is DOING something before
        # asserting the two sides agree.
        self.assertTrue(md, "STRUCT01 produced no findings at all — the call is not exercising it")
        self.assertEqual(
            md,
            ya,
            "STRUCT01 reports a different missing-section set per carrier for identical content",
        )
        # Both fixtures declare these two; neither carrier may report them missing.
        for present in ("functional_requirements", "traceability"):
            with self.subTest(section=present):
                self.assertNotIn(present, md, "a section present on both carriers was flagged")


if __name__ == "__main__":
    unittest.main()
