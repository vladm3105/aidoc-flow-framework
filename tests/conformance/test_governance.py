"""Conformance: ``framework/governance/`` files are present and parseable."""

import unittest

import yaml

from _spec import ARTIFACTS, FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"

EXPECTED_FILES = [
    "DOC_GOVERNANCE_CORE.md",
    "ID_NAMING_STANDARDS.md",
    "TRACEABILITY.md",
    "DIAGRAM_STANDARDS.md",
    "THRESHOLD_NAMING_RULES.md",
    "ADAPTATION.md",
    "ADAPTATION_SURFACE.yaml",
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

    def test_no_project_adaptation_artifacts_in_framework(self):
        """A consuming project's adaptation profile/learnings must never be
        committed under framework/ — the spec ships the contract, not project
        data (ADAPTATION.md; D-0013)."""
        leaked = [
            p.relative_to(FRAMEWORK).as_posix()
            for p in FRAMEWORK.rglob("*")
            if p.is_file()
            and (".aidoc" in p.parts or p.name in ("profile.yaml", "learnings.md"))
        ]
        self.assertEqual(leaked, [], f"project adaptation artifacts under framework/: {leaked}")

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

    def test_adaptation_surface_is_well_formed(self):
        """The adaptation surface parses, declares a closed unique knob set,
        and the mandatory/skippable layer split partitions a subset of the 8
        artifacts (ADAPTATION.md)."""
        with (GOVERNANCE / "ADAPTATION_SURFACE.yaml").open(encoding="utf-8") as fh:
            surface = yaml.safe_load(fh)
        names = [k["name"] for k in surface["knobs"]]
        self.assertTrue(names, "no knobs declared")
        self.assertEqual(len(names), len(set(names)), f"duplicate knob names: {names}")

        mandatory = set(surface["layers"]["mandatory"])
        skippable = set(surface["layers"]["skippable"])
        self.assertEqual(mandatory & skippable, set(), "layer is both mandatory and skippable")
        self.assertLessEqual(
            mandatory | skippable, set(ARTIFACTS),
            "adaptation layer split references an unknown artifact",
        )


if __name__ == "__main__":
    unittest.main()
