"""Deterministic acceptance: Layer 6 — SPEC."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerSpecTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 6
    LAYER_NAME = "SPEC"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "SPEC-01_golden.yaml"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_parses_as_yaml_with_metadata_layer_6(self):
        with self.golden.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        self.assertIsInstance(data, dict, "SPEC-01: golden must parse to a YAML mapping")
        self.assertIn("metadata", data, "SPEC-01: missing 'metadata' key")
        self.assertEqual(
            data["metadata"].get("layer"),
            6,
            f"SPEC-01: metadata.layer={data['metadata'].get('layer')}; expected 6",
        )


if __name__ == "__main__":
    unittest.main()
