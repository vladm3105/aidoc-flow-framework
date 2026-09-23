"""Deterministic acceptance: Layer 10 — EVAL.

The EVAL template carries no `required_environment` / `test_data_setup` /
`coverage_tracking` / `test_results` keys (those live on the REPORT template
§4 or in CI) — D5 records the gap as a downgrade rather than minting new
contract here (#670).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import FIXTURES_ROOT, LayerHarness


class LayerEvalTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 10
    LAYER_NAME = "EVAL"

    def setUp(self):
        # fixtures_for() covers the 8 document layers; CHG/EVAL resolve here.
        self.valid = FIXTURES_ROOT / "layer_10_eval" / "valid"
        self.broken = FIXTURES_ROOT / "layer_10_eval" / "broken"
        self.golden = self.valid / "EVAL-01_golden.yaml"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)


if __name__ == "__main__":
    unittest.main()
