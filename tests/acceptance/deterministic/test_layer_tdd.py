"""Deterministic acceptance: Layer 7 — TDD."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for, load_layer_document

REPO_ROOT = Path(__file__).resolve().parents[3]


def _template_test_types() -> set:
    """Case-type vocabulary, derived from the template (single source, #670 D5)."""
    doc = yaml.safe_load(
        (REPO_ROOT / "framework" / "layers" / "07_TDD" / "TDD-TEMPLATE.yaml").read_text(
            encoding="utf-8"
        )
    )
    return set(doc["test_strategy"]["test_types"])


VALID_TYPES = _template_test_types()


class LayerTddTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 7
    LAYER_NAME = "TDD"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "TDD-01_golden.yaml"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_every_test_case_has_a_valid_type(self):
        data = load_layer_document(self.golden)
        cases = (data.get("test_cases") or {}).get("cases") or []
        self.assertGreaterEqual(
            len(cases),
            1,
            "TDD-01: §test_cases.cases must define at least one case",
        )
        for idx, case in enumerate(cases):
            self.assertIn(
                "id",
                case,
                f"TDD-01 case[{idx}]: missing 'id'",
            )
            self.assertIn(
                "spec_ref",
                case,
                f"TDD-01 case[{idx}] {case.get('id')}: missing 'spec_ref'",
            )
            case_type = case.get("type")
            self.assertIn(
                case_type,
                VALID_TYPES,
                f"TDD-01 case[{idx}] {case.get('id')}: type='{case_type}' not in {sorted(VALID_TYPES)}",
            )


if __name__ == "__main__":
    unittest.main()
