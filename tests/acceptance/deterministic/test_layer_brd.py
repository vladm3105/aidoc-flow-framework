"""Deterministic acceptance: Layer 1 — BRD."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerBrdTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 1
    LAYER_NAME = "BRD"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "BRD-01_golden.md"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_no_upstream_tags_on_layer_one(self):
        text = self.golden.read_text(encoding="utf-8")
        for tag in ("@brd:", "@prd:", "@ears:", "@bdd:", "@adr:", "@spec:", "@tdd:"):
            self.assertNotIn(tag, text, f"{self.golden.name} has unexpected upstream tag {tag}")


if __name__ == "__main__":
    unittest.main()
