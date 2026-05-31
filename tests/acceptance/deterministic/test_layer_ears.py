"""Deterministic acceptance: Layer 3 — EARS."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerEarsTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 3
    LAYER_NAME = "EARS"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "EARS-01_golden.md"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_every_requirement_uses_canonical_ears_form(self):
        """Every H3 in §Requirements must use the WHEN ... THE ... SHALL ... WITHIN ... form."""
        text = self.golden.read_text(encoding="utf-8")
        match = re.search(
            r"^##\s+Requirements\s*$(.*?)(?=^##\s|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, "EARS-01: §Requirements section not found")
        body = match.group(1)
        # Split body into per-H3 blocks; the first piece before any H3 is preamble.
        pieces = re.split(r"(?m)^###\s+.+$", body)
        h3_titles = re.findall(r"(?m)^###\s+(.+)$", body)
        self.assertGreaterEqual(
            len(h3_titles),
            2,
            f"EARS-01 §Requirements: expected >=2 requirements, got {len(h3_titles)}",
        )
        canonical = re.compile(
            r"\bWHEN\b.+?\bTHE\b.+?\bSHALL\b.+?\bWITHIN\b",
            re.IGNORECASE | re.DOTALL,
        )
        # pieces[0] is preamble before first H3; pieces[1..] correspond to h3_titles.
        for title, block in zip(h3_titles, pieces[1:]):
            self.assertRegex(
                block,
                canonical,
                f"EARS-01 §Requirements '{title}': not in WHEN/THE/SHALL/WITHIN canonical form",
            )


if __name__ == "__main__":
    unittest.main()
