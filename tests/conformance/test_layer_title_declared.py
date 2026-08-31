"""Conformance: every full layer template declares a scalar top-level ``title:``.

Three of the eight full templates — SPEC, TDD and IPLAN — declared no document
title at all, while every artifact they produce carries one, authored by hand in
a key the template never named. `IPLAN-SELF-DESCRIPTION-001` (#553) closes that;
this module pins the class so a ninth layer cannot arrive without a title.

**Why the value's TYPE is asserted, not merely the key's presence.** Two
independent derivations read a layer template's top-level keys and they disagree
about what a section is:

1. ``sdd_doc_lint._load_section_targets`` admits a key only when its value is a
   mapping carrying an integer ``_size_target``. A scalar ``title:`` fails the
   ``isinstance(body, dict)`` test and is skipped, so ``STRUCT01``'s derived
   required set does not move.
2. ``tests.acceptance._harness.template_sections`` admits **every** top-level key
   whose value is a mapping and whose name is not ``metadata`` — it does *not*
   require ``_size_target`` — and asserts the result against each golden's
   headings.

So a ``title:`` authored as a mapping (the pervasive convention in these very
templates, where ``_guidance:`` children are everywhere) would leave the
conformance tier **green** while the acceptance tier went **red** with
``missing template sections ['title']`` on three goldens. A presence-only guard
passes that mutant; this one does not.

BRD is the standing proof the scalar form is inert: it has carried a top-level
``title:`` since before either pin existed and still derives 17 required
sections.

The roster is iterated from ``ARTIFACTS`` directly rather than from a local
literal, so adding a layer to the registry without a title fails here. (Note the
sibling pin's ``test_derived_required_counts_match_the_pins`` loops a
module-local dict, which is right for *its* purpose — pinning values a diff must
justify — and wrong for this one.)
"""

from __future__ import annotations

import unittest

import yaml
from _spec import ARTIFACTS, FRAMEWORK

# MVP templates are deliberately excluded: they carry `document_control.title`,
# a different and internally uniform convention across all eight layers.
# Reconciling the two sets is `IPLAN-LAYER-REVIEW-001-DESIGN.md` R9, not this.
TEMPLATE_GLOB = "*/{artifact}-TEMPLATE.yaml"


def _template_path(artifact: str):
    return next(FRAMEWORK.joinpath("layers").glob(TEMPLATE_GLOB.format(artifact=artifact)))


def _load(artifact: str) -> dict:
    with _template_path(artifact).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


class EveryLayerTemplateDeclaresATitle(unittest.TestCase):
    def test_every_artifact_has_a_full_template(self):
        """The roster is complete, so a new layer cannot slip past this module."""
        for artifact in ARTIFACTS:
            with self.subTest(artifact=artifact):
                self.assertTrue(
                    _template_path(artifact).is_file(),
                    f"{artifact}: no full template found under framework/layers/",
                )

    def test_title_is_declared_at_top_level(self):
        for artifact in ARTIFACTS:
            with self.subTest(artifact=artifact):
                doc = _load(artifact)
                self.assertIn(
                    "title",
                    doc,
                    f"{artifact}-TEMPLATE.yaml declares no top-level `title:`. Every "
                    "artifact this template produces carries one; the template has to "
                    "name it. Place it above `metadata:`, matching the five layers "
                    "that already do (IPLAN-SELF-DESCRIPTION-001, #553).",
                )

    def test_title_is_a_non_empty_scalar_string(self):
        """A mapping `title:` is green here-adjacent but red in the acceptance tier.

        `tests/acceptance/_harness.template_sections` treats any top-level mapping
        that is not `metadata` as a section and asserts it against the goldens, so
        the mapping form fails there with a message that never mentions `title`'s
        type. Catch it at the source instead.
        """
        for artifact in ARTIFACTS:
            with self.subTest(artifact=artifact):
                title = _load(artifact).get("title")
                self.assertIsInstance(
                    title,
                    str,
                    f"{artifact}-TEMPLATE.yaml `title:` must be a plain scalar string, "
                    f"not {type(title).__name__}. A mapping value would be read as a "
                    "SECTION by tests/acceptance/_harness.template_sections and redden "
                    "every golden for this layer, while STRUCT01 stayed green.",
                )
                self.assertTrue(
                    str(title).strip(),
                    f"{artifact}-TEMPLATE.yaml `title:` is empty",
                )

    def test_title_does_not_join_the_struct01_required_set(self):
        """The invariant behind the scalar rule, asserted as an invariant.

        Stated separately from the type check because it is the *reason* for it:
        a future edit that made `title` section-shaped would break this before it
        broke a golden, and the failure would say why.
        """
        import sys

        sys.path.insert(0, str(FRAMEWORK.parent / "tools"))
        from sdd_doc_lint import _load_section_targets  # noqa: PLC0415

        for artifact in ARTIFACTS:
            with self.subTest(artifact=artifact):
                self.assertNotIn(
                    "title",
                    _load_section_targets(artifact),
                    f"{artifact}: `title` entered STRUCT01's derived required-section "
                    "set. It is document identity, not a section — this means the key "
                    "grew a mapping value carrying `_size_target`.",
                )


if __name__ == "__main__":
    unittest.main()
