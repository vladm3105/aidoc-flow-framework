"""Deterministic acceptance: Layer 5 — ADR."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for

VALID_STATUSES = {"Proposed", "Accepted", "Superseded", "Deprecated"}


class LayerAdrTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 5
    LAYER_NAME = "ADR"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "ADR-01_golden.md"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_status_is_a_valid_adr_status(self):
        text = self.golden.read_text(encoding="utf-8")
        match = re.search(r"(?m)^[*\-]?\s*Status:\s*(\w+)", text)
        self.assertIsNotNone(match, "ADR-01: no 'Status:' line found in body")
        status = match.group(1)
        self.assertIn(
            status,
            VALID_STATUSES,
            f"ADR-01: status='{status}' not in {sorted(VALID_STATUSES)}",
        )


if __name__ == "__main__":
    unittest.main()
