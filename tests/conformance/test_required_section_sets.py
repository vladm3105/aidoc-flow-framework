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

import yaml
from _spec import ARTIFACTS, FRAMEWORK, REPO_ROOT

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

# The section NAMES, not just how many. The count pin alone cannot see an
# identity-preserving rename: measured on OPS-0065 round 4, renaming a template
# key failed ZERO tests in this module (it died only via unrelated lint-runtime
# and acceptance guards). The module docstring claimed it "pins both" directions;
# without this it pinned one.
SECTIONS: dict[str, frozenset] = {
    "BRD": frozenset(
        [
            "acceptance_criteria",
            "adr_topics",
            "appendix",
            "approval",
            "business_objectives",
            "constraints_and_assumptions",
            "diagrams",
            "document_control",
            "executive_summary",
            "functional_requirements",
            "glossary",
            "introduction",
            "project_scope",
            "quality_expectations",
            "risk_management",
            "stakeholders",
            "traceability",
        ]
    ),
    "PRD": frozenset(
        [
            "acceptance_criteria",
            "constraints_and_assumptions",
            "customer_facing_content",
            "document_control",
            "executive_summary",
            "functional_requirements",
            "glossary",
            "goals_and_objectives",
            "problem_statement",
            "risk_assessment",
            "scope_and_requirements",
            "success_metrics",
            "target_audience",
            "traceability",
            "user_stories",
        ]
    ),
    "EARS": frozenset(
        [
            "document_control",
            "glossary",
            "purpose_and_context",
            "quality_attributes",
            "requirements",
            "traceability",
        ]
    ),
    "BDD": frozenset(
        ["document_control", "feature_definition", "glossary", "scenario_structure", "traceability"]
    ),
    "ADR": frozenset(
        [
            "alternatives",
            "appendix",
            "architecture_flow",
            "consequences",
            "context",
            "decision",
            "document_control",
            "glossary",
            "implementation_assessment",
            "related_decisions",
            "traceability",
            "verification",
        ]
    ),
    "SPEC": frozenset(
        [
            "behavior",
            "component_overview",
            "data_models",
            "document_control",
            "implementation_notes",
            "interfaces",
            "tdd_contracts",
            "traceability",
        ]
    ),
    "TDD": frozenset(
        [
            "document_control",
            "tdd_order",
            "test_cases",
            "test_mapping",
            "test_pyramid",
            "thresholds",
            "traceability",
        ]
    ),
    "IPLAN": frozenset(["document_control", "traceability"]),
}

# The DECLARED half — `metadata.total_sections`, the numbered-section count.
# GD-21 ratifies that these two numbers are different measurements and may
# legitimately disagree; until this pin existed, GD-21 was prose with no
# executable consumer and an edit to any `total_sections:` passed the whole tier
# (measured on OPS-0065 round 3: EARS 5→9 and ADR 10→12 both SURVIVED).
DECLARED = {
    "BRD": 16,
    "PRD": 15,
    "EARS": 5,
    "BDD": 5,
    "ADR": 10,
    "SPEC": 8,
    "TDD": 7,
    "IPLAN": 6,
}

# Layers whose required set legitimately exceeds their `total_sections`, because
# they carry required UNNUMBERED backmatter. Pinned as a set so that a layer
# joining or leaving this class is a deliberate, visible edit — #557 misread
# membership of it as a defect.
#
# ⚠️ This is NOT "the layers whose two numbers differ". IPLAN's differ too, in the
# opposite direction (2 derived vs 6 declared, because 9 of its 11 `_size_target`
# keys are `_required: false` / `_required_when_subtype:`). `test_backmatter_class_is_derived_not_asserted`
# below derives this set from `derived > declared` so the frozenset cannot drift
# from the templates — before that test existed this constant was referenced by
# nothing and enforced nothing despite the comment above claiming it did.
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

    def _declared(self, layer: str) -> int:
        path = next(FRAMEWORK.joinpath("layers").glob(f"*/{layer}-TEMPLATE.yaml"))
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return (data.get("metadata") or {}).get("total_sections")

    def test_declared_total_sections_match_the_pins(self):
        """GD-21's DECLARED half, which had no executable consumer at all.

        `total_sections` is read by exactly one other test in the repo
        (`test_seed_contract.py`, BRD-only), so before this pin an edit to any
        template's `total_sections:` passed the entire conformance tier. Measured
        on OPS-0065 round 3: EARS 5 -> 9 and ADR 10 -> 12 both SURVIVED 449 tests.
        """
        for layer in sorted(DECLARED):
            with self.subTest(layer=layer):
                self.assertEqual(
                    DECLARED[layer],
                    self._declared(layer),
                    f"{layer}: metadata.total_sections moved; GD-21 pins it because it is a "
                    "different measurement from STRUCT01's derived set, not a copy of it",
                )

    def test_backmatter_class_is_derived_not_asserted(self):
        """`BACKMATTER_LAYERS` was referenced by no code and enforced nothing.

        Its comment claimed a layer joining or leaving the class would be "a
        deliberate, visible edit". It could not be: nothing read the set. This
        derives the class from the templates and pins it, so the constant and the
        contract cannot drift apart.

        Asserts the DIRECTION, not just membership: a layer is backmatter-bearing
        when its derived set EXCEEDS its declared count. IPLAN's two numbers also
        differ (2 vs 6) but in the opposite direction, so a membership test written
        as `derived != declared` would wrongly admit it -- which is the exact
        misreading GD-21 exists to prevent.
        """
        exceeds = {
            layer for layer in DECLARED if len(_load_section_targets(layer)) > self._declared(layer)
        }
        self.assertEqual(
            BACKMATTER_LAYERS,
            exceeds,
            "the layers whose derived set exceeds total_sections no longer match "
            "BACKMATTER_LAYERS; update the constant deliberately or fix the template",
        )
        below = {
            layer for layer in DECLARED if len(_load_section_targets(layer)) < self._declared(layer)
        }
        self.assertEqual(
            {"IPLAN"},
            below,
            "IPLAN is the only layer expected to derive FEWER sections than it "
            "declares; a new one means an unmarked optional-section change",
        )

    def test_derived_section_names_match_the_pins(self):
        """The identity half. A rename is a contract change and must be visible here."""
        for layer in sorted(SECTIONS):
            with self.subTest(layer=layer):
                self.assertEqual(
                    SECTIONS[layer],
                    frozenset(_load_section_targets(layer)),
                    f"{layer}: the SET of required sections changed, not just the count — "
                    "a renamed or swapped template key changes what STRUCT01 enforces",
                )

    def test_the_two_pins_agree(self):
        """Guards the guard: EXPECTED is the size of SECTIONS, or one of them is stale."""
        self.assertEqual(
            {k: len(v) for k, v in SECTIONS.items()},
            EXPECTED,
            "SECTIONS and EXPECTED disagree — update both in the same edit",
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
