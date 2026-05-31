"""Deterministic acceptance: Layer 2 — PRD."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerPrdTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 2
    LAYER_NAME = "PRD"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "PRD-01_golden.md"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_customer_facing_content_has_at_least_3_substantive_categories(self):
        text = self.golden.read_text(encoding="utf-8")
        match = re.search(
            r"^##\s+Customer[- ]Facing.*?$(.*?)(?=^##\s|\Z)",
            text,
            re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )
        self.assertIsNotNone(match, "PRD-01: §10 Customer-Facing Content not found")
        body = match.group(1)
        categories = re.findall(r"^###\s+(.+)$", body, re.MULTILINE)
        substantive = [
            c
            for c in categories
            if re.search(rf"^###\s+{re.escape(c)}\s*\n\s*[A-Za-z]", body, re.MULTILINE)
        ]
        self.assertGreaterEqual(
            len(substantive),
            3,
            f"PRD-01 §10: need >=3 substantive categories, got {substantive}",
        )


if __name__ == "__main__":
    unittest.main()
