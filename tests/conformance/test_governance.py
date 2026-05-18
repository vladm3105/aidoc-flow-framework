"""Conformance: ``framework/governance/`` files are present and parseable."""

import unittest

import yaml

from _spec import FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"

EXPECTED_FILES = [
    "DOC_GOVERNANCE_CORE.md",
    "ID_NAMING_STANDARDS.md",
    "TRACEABILITY.md",
    "DIAGRAM_STANDARDS.md",
    "THRESHOLD_NAMING_RULES.md",
    "README.md",
    "chg/README.md",
    "chg/CHG-TEMPLATE.yaml",
    "chg/CHG-00_index.TEMPLATE.md",
    "chg/gates/GATE-01_BUSINESS_PRODUCT.md",
    "chg/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md",
    "chg/gates/GATE-06_DESIGN_TEST.md",
    "chg/gates/GATE-08_IPLAN.md",
    "chg/gates/GATE-CODE_IMPLEMENTATION.md",
    "chg/gates/GATE_ERROR_CATALOG.md",
    "chg/gates/GATE_INTERACTION_DIAGRAM.md",
    "chg/templates/GATE_APPROVAL_FORM.md",
    "chg/templates/POST_MORTEM-TEMPLATE.md",
]


class GovernanceFiles(unittest.TestCase):
    def test_expected_files_present(self):
        for relative in EXPECTED_FILES:
            with self.subTest(file=relative):
                self.assertTrue(
                    (GOVERNANCE / relative).is_file(),
                    f"missing governance file: {relative}",
                )

    def test_no_unexpected_files(self):
        found = {
            p.relative_to(GOVERNANCE).as_posix()
            for p in GOVERNANCE.rglob("*")
            if p.is_file()
        }
        self.assertEqual(found, set(EXPECTED_FILES))

    def test_chg_template_parses(self):
        with (GOVERNANCE / "chg" / "CHG-TEMPLATE.yaml").open(encoding="utf-8") as fh:
            self.assertIsNotNone(yaml.safe_load(fh))


if __name__ == "__main__":
    unittest.main()
