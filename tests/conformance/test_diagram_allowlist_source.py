"""Conformance: DG02's allowlist comes from the registry, and the registry is read.

`LAYER_REGISTRY.yaml` carries `c4_mapping[*].diagram_tags` and the registry's own
README calls itself the single source of truth — but **no code read that field**.
`DG02`'s real authority was a literal in `tools/sdd_doc_lint`, making the diagram
vocabulary a five-surface statement with the executable one last (#552).

That is the third instance of one shape this session: #565 (`extensions` is the
normative instance-format field and no linter reads it) and #531 (a granularity
rule stated in four places, executable in one). The pattern is a
machine-readable field that *looks* authoritative and is consumed by nothing.

`_diagram_allowed()` now reads the registry, with the literal kept only as a
fallback for an unreadable registry — the direction that fails safe, since an
empty allowlist makes `DG02` **reject** rather than accept.
"""

from __future__ import annotations

import sys
import unittest

import yaml
from _spec import REGISTRY_PATH, REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import _DIAGRAM_ALLOWED, _diagram_allowed  # noqa: E402

LAYERS = ("BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN")


class DiagramAllowlistComesFromTheRegistry(unittest.TestCase):
    def test_the_registry_declares_diagram_tags(self):
        """Guards the guard: with the field gone, every assertion below is vacuous."""
        data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
        mapping = data.get("c4_mapping")
        self.assertIsInstance(mapping, dict, "LAYER_REGISTRY.yaml lost its c4_mapping block")
        self.assertTrue(
            any("diagram_tags" in e for e in mapping.values() if isinstance(e, dict)),
            "no c4_mapping entry declares diagram_tags — DG02 would silently fall back",
        )

    def test_every_layer_resolves_through_the_registry(self):
        for layer in LAYERS:
            with self.subTest(layer=layer):
                self.assertIsInstance(_diagram_allowed(layer), set)

    def test_registry_and_fallback_agree(self):
        """The consolidation invariant, and the reason this was safe to land.

        `sequence-*` is excluded from the comparison because `_DIAGRAM_SEQUENCE`
        allows it on **every** layer regardless of the allowlist — PRD's registry
        entry lists `sequence-sync`, which the literal omits, and the two are
        therefore equivalent in effect rather than identical in content.

        A divergence here is not automatically a defect: it means the registry
        and the fallback disagree, and whoever changed one must say which is
        right. Failing is how that decision gets made deliberately.
        """
        for layer in LAYERS:
            with self.subTest(layer=layer):
                from_registry = {
                    t for t in _diagram_allowed(layer) if not t.startswith("sequence-")
                }
                self.assertEqual(
                    from_registry,
                    _DIAGRAM_ALLOWED.get(layer, set()),
                    f"{layer}: registry diagram_tags and the in-code fallback disagree",
                )

    def test_an_unreadable_registry_fails_closed(self):
        """Falls back to the literal, never to 'allow everything'.

        An allowlist that widens on error is the dangerous direction: DG02 would
        stop rejecting and the failure would be invisible.
        """
        from pathlib import Path

        self.assertEqual(
            _diagram_allowed("BRD", Path("/nonexistent/LAYER_REGISTRY.yaml")),
            _DIAGRAM_ALLOWED["BRD"],
        )


if __name__ == "__main__":
    unittest.main()
