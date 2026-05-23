"""Conformance: the GATE-SPEC diff-aware guard stays in sync with the gate.

``tests/chg/spec_gate.py`` is the CI-side enforcement of the diff-aware
GATE-SPEC codes (E005, E008). This guard keeps it importable and consistent with
the gate definition in the spec, so the two cannot drift apart silently.
"""

import importlib.util
import unittest
from pathlib import Path

from _spec import FRAMEWORK

SPEC_GATE = Path(__file__).resolve().parents[1] / "chg" / "spec_gate.py"
CATALOG = FRAMEWORK / "governance" / "chg" / "gates" / "GATE_ERROR_CATALOG.md"


def _load_spec_gate():
    spec = importlib.util.spec_from_file_location("spec_gate", SPEC_GATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SpecGateGuard(unittest.TestCase):
    def test_script_present_and_importable(self):
        self.assertTrue(SPEC_GATE.is_file(), f"missing {SPEC_GATE}")
        module = _load_spec_gate()
        self.assertTrue(hasattr(module, "CODES"), "spec_gate must declare CODES")

    def test_owned_codes_match_the_gate(self):
        module = _load_spec_gate()
        self.assertEqual(
            set(module.CODES), {"GATE-SPEC-E005", "GATE-SPEC-E008"},
            "spec_gate owns exactly the two diff-aware GATE-SPEC codes",
        )
        catalog = CATALOG.read_text(encoding="utf-8")
        for code in module.CODES:
            self.assertIn(code, catalog, f"{code} owned by spec_gate but absent from the error catalog")

    def test_non_spec_change_is_a_noop(self):
        module = _load_spec_gate()
        self.assertEqual(module.evaluate(["README.md", "platforms/x/SKILL.md"]), [])

    def test_spec_change_without_version_or_changelog_fails(self):
        module = _load_spec_gate()
        failures = module.evaluate(["framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md"])
        self.assertEqual(set(failures), {"GATE-SPEC-E005", "GATE-SPEC-E008"})

    def test_compliant_spec_change_passes(self):
        module = _load_spec_gate()
        failures = module.evaluate(
            ["framework/VERSION", "framework/governance/ADAPTATION.md", "CHANGELOG.md"]
        )
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
