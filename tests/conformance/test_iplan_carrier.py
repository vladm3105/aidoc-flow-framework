"""Conformance: both IPLAN templates carry the `tdd_ref` TDD-case carrier.

IPLAN-TDDREF-001. The carrier is the key a downstream coverage rule matches on one
line (the analogue of the TDD layer's `bdd_ref`). Nothing else locks it:
`test_seed_contract.py`'s MVP-skeleton precedent is BRD-scoped, and
`test_element_id_layer_contract.py` explicitly excludes `*-MVP-TEMPLATE.yaml`. Without
this guard, dropping the field from either template stays green.

Both templates are asserted, not just the skeleton: the canonical template is exactly
as unguarded as the MVP one.

The asserts PARSE the YAML rather than grepping — a substring check for `tdd_ref` is
satisfied by the unrelated `tdd_references:` key in the traceability section.
"""

import re
import unittest
from pathlib import Path

import yaml

FRAMEWORK = Path(__file__).resolve().parents[2] / "framework"
LAYER = FRAMEWORK / "layers" / "08_IPLAN"
CARRIER = "tdd_ref"


def _entries(doc: dict) -> list:
    """The manifest entries, across both shapes.

    The canonical template nests them under `file_manifest.files`; the MVP skeleton
    makes `file_manifest` a bare list. That divergence is tracked separately (the
    carrier is line-local, so it attaches either way) — this helper tolerates both so
    the guard does not silently pass by finding nothing to check.
    """
    manifest = doc.get("file_manifest")
    if isinstance(manifest, list):
        return [e for e in manifest if isinstance(e, dict)]
    if isinstance(manifest, dict):
        return [e for e in manifest.get("files") or [] if isinstance(e, dict)]
    return []


class IplanCarrier(unittest.TestCase):
    def _assert_carrier(self, name: str):
        path = LAYER / name
        self.assertTrue(path.is_file(), f"missing template: {path}")
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        entries = _entries(doc)
        self.assertTrue(entries, f"{name}: no file-manifest entries found to check")
        carried = [e for e in entries if CARRIER in e]
        self.assertTrue(
            carried,
            f"{name}: no file_manifest entry carries `{CARRIER}` — the TDD-case "
            "carrier a downstream coverage rule matches on (IPLAN-TDDREF-001)",
        )
        for entry in carried:
            value = entry[CARRIER]
            self.assertIsInstance(value, str, f"{name}: `{CARRIER}` must be a scalar")
            self.assertIn(
                "@tdd:",
                value,
                f"{name}: `{CARRIER}` must hold the tag as its value — a downstream "
                "matcher reads the key and the tag from ONE line",
            )

    def test_canonical_template_carries_tdd_ref(self):
        self._assert_carrier("IPLAN-TEMPLATE.yaml")

    def test_mvp_skeleton_carries_tdd_ref(self):
        self._assert_carrier("IPLAN-MVP-TEMPLATE.yaml")

    def test_traceability_key_is_still_named_tdd_references(self):
        """A positive assertion, because the negative one was unfalsifiable.

        The first version scanned for lines containing `tdd_references` and
        asserted the carrier regex did not match them — which passes for ANY file
        content (the trailing `e` always defeats `\btdd_ref\b`), and which goes
        vacuous under the very rename it claimed to catch, because the guard is
        conditioned on the string whose disappearance is the defect.

        Assert the property positively instead: the traceability key is spelled
        `tdd_references`, so a `\btdd_ref\b` matcher cannot confuse the two.
        """
        doc = yaml.safe_load((LAYER / "IPLAN-TEMPLATE.yaml").read_text(encoding="utf-8"))
        upstream = (doc.get("traceability") or {}).get("upstream") or {}
        self.assertIn(
            "tdd_references",
            upstream,
            "traceability.upstream no longer declares `tdd_references` — if it was "
            f"renamed to `{CARRIER}`, the carrier stops being discriminating",
        )

    def test_carrier_regex_cannot_match_the_traceability_key(self):
        """The regex property itself, with no file dependency.

        This is what a downstream matcher relies on; it holds or fails on its own
        terms rather than on what happens to be in a template today.
        """
        matcher = re.compile(r"\btdd_ref\b")
        self.assertIsNone(matcher.search("  tdd_references:"))
        self.assertIsNotNone(matcher.search('      tdd_ref: "@tdd: TDD.01.04.aaaa"'))


if __name__ == "__main__":
    unittest.main()
