"""Conformance: each layer's derived required-section set is pinned, per layer.

`STRUCT01`'s required set is **derived**, not declared — every top-level template
key carrying `_size_target`, minus those marked `_required: false` or
`_required_when_subtype:`. So a one-line marker edit in a template silently moves
what the framework enforces, in either direction, and no existing check notices:

* a marker **added** removes a required section. The acceptance suite keeps
  passing, because a golden that still carries the section satisfies a smaller
  assertion — the "a fix can silently disarm an existing regression test" trap.
* a marker **removed** adds one, which at least fails loudly on the goldens.

The additive direction is guarded by the goldens; the subtractive one was
guarded by nothing. This module pins both.

**Regression cover: #557.** That issue reported EARS deriving six required
sections against a declared `total_sections: 5`, and proposed marking
`glossary:` `_required: false`. The change was staged and reverted here on
measurement, and both halves of its premise were wrong:

1. It stated that no EARS artifact has a glossary section. Both do —
   ``tests/acceptance/fixtures/layer_03_ears/valid/EARS-01_golden.md`` and
   ``examples/url-shortener/docs/03_EARS/EARS-01.md``. The marker would have
   removed a live assertion, not a latent one.
2. It treated EARS as the outlier. It is not: ``total_sections`` counts
   **numbered** sections, while the derived set counts **required** ones and
   includes required unnumbered backmatter. BRD (17 against 16) and ADR (12
   against 10) have exactly the same shape for exactly the same reason. SPEC and
   TDD agree only because they carry no backmatter.

`_required: false` means *optional content* — PRD's `component_decomposition` is
"only required when downstream cites `@threshold`". It does not mean "required
but unnumbered", and asking it to carry both senses is what produced #557.
"""

from __future__ import annotations

import sys
import unittest

from _spec import ARTIFACTS, REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import _load_section_targets  # noqa: E402

# The pinned sets. Held as literals — a derived expectation would move with the
# templates and assert nothing. Changing one of these is the point at which a
# contributor has to say, in a diff, that they meant to change what the
# framework enforces.
EXPECTED = {
    "BRD": 17,
    "PRD": 15,
    "EARS": 6,
    "BDD": 5,
    "ADR": 12,
    "SPEC": 8,
    "TDD": 7,
    "IPLAN": 2,
}

# Layers whose required set legitimately exceeds their `total_sections`, because
# they carry required UNNUMBERED backmatter. Pinned as a set so that a layer
# joining or leaving this class is a deliberate, visible edit — #557 misread
# membership of it as a defect.
BACKMATTER_LAYERS = frozenset({"BRD", "EARS", "ADR"})


class RequiredSectionSetsArePinned(unittest.TestCase):
    def test_every_layer_is_pinned(self):
        """The roster is complete, so a new layer cannot slip in unpinned."""
        self.assertEqual(set(EXPECTED), set(ARTIFACTS))

    def test_derived_required_counts_match_the_pins(self):
        for layer in sorted(EXPECTED):
            with self.subTest(layer=layer):
                got = sorted(_load_section_targets(layer))
                self.assertEqual(
                    len(got),
                    EXPECTED[layer],
                    f"{layer}: STRUCT01 now requires {len(got)} sections, pinned at "
                    f"{EXPECTED[layer]} — {got}. If deliberate, update the pin in the "
                    "same commit and say why; a `_required: false` marker added to a "
                    "template silently removes an assertion the goldens still satisfy.",
                )

    def test_ears_still_requires_its_glossary(self):
        """#557's specific regression, named rather than left implicit.

        Asserted separately from the count so the failure message says *what*
        changed rather than *how many*, and so a compensating edit elsewhere in
        the template cannot keep the count at 6 while dropping this key.
        """
        self.assertIn(
            "glossary",
            _load_section_targets("EARS"),
            "EARS's glossary is required backmatter — the plugin authoring skill "
            "calls it required and both EARS artifacts carry it. See #557.",
        )


if __name__ == "__main__":
    unittest.main()
