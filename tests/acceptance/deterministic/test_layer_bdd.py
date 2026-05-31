"""Deterministic acceptance: Layer 4 — BDD."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerBddTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 4
    LAYER_NAME = "BDD"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "BDD-01_golden.md"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_every_scenario_has_given_when_then(self):
        """Every Scenario block in §Scenario Structure must use Given/When/Then."""
        text = self.golden.read_text(encoding="utf-8")
        match = re.search(
            r"^##\s+Scenario Structure\s*$(.*?)(?=^##\s|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, "BDD-01: §Scenario Structure section not found")
        body = match.group(1)
        scenarios = re.split(r"(?m)^###\s+.+$", body)
        titles = re.findall(r"(?m)^###\s+(.+)$", body)
        self.assertGreaterEqual(
            len(titles),
            2,
            f"BDD-01 §Scenario Structure: expected >=2 scenarios, got {len(titles)}",
        )
        for title, block in zip(titles, scenarios[1:]):
            for keyword in ("Given", "When", "Then"):
                self.assertRegex(
                    block,
                    rf"\b{keyword}\b",
                    f"BDD-01 §Scenario Structure '{title}': missing {keyword} step",
                )


if __name__ == "__main__":
    unittest.main()
