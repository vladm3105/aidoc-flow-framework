"""Conformance: ``framework/governance/`` files are present and parseable."""

import unittest

import yaml
from _spec import ARTIFACTS, FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"

EXPECTED_FILES = [
    "DOC_GOVERNANCE_CORE.md",
    "FRAMEWORK_FEEDBACK_LOG.md",
    "ID_NAMING_STANDARDS.md",
    "TRACEABILITY.md",
    "TAG_SYNTAX.md",
    "DIAGRAM_STANDARDS.md",
    "THRESHOLD_NAMING_RULES.md",
    "SECURITY_REVIEW.md",
    "REVIEW_REMEDIATION_FLOW.md",
    "DEFINITION_OF_DONE.md",
    "REVIEW_TEAM.md",
    "REVIEW_CREWS.yaml",
    "REVIEW_SAGA.md",
    "saga.schema.json",
    "ADAPTATION.md",
    "ADAPTATION_SURFACE.yaml",
    "PROFILE-TEMPLATE.yaml",
    "AUTHORING_STYLE.md",
    "DECISIONS.md",
    "README.md",
    "chg/README.md",
    "chg/CHG-TEMPLATE.yaml",
    "chg/CHG-00_index.TEMPLATE.md",
    "chg/gates/GATE-01_BUSINESS_PRODUCT.md",
    "chg/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md",
    "chg/gates/GATE-06_DESIGN_TEST.md",
    "chg/gates/GATE-08_IPLAN.md",
    "chg/gates/GATE-CODE_IMPLEMENTATION.md",
    "chg/gates/GATE-SPEC_FRAMEWORK.md",
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
            if p.is_file() and (".aidoc" in p.parts or p.name in ("profile.yaml", "learnings.md"))
        ]
        self.assertEqual(leaked, [], f"project adaptation artifacts under framework/: {leaked}")

    def test_no_unexpected_files(self):
        found = {p.relative_to(GOVERNANCE).as_posix() for p in GOVERNANCE.rglob("*") if p.is_file()}
        self.assertEqual(found, set(EXPECTED_FILES))

    def test_chg_template_parses(self):
        with (GOVERNANCE / "chg" / "CHG-TEMPLATE.yaml").open(encoding="utf-8") as fh:
            self.assertIsNotNone(yaml.safe_load(fh))

    def test_spec_gate_is_wired(self):
        """GATE-SPEC (the framework-spec change gate, CHG-D1) is declared
        consistently across the gate def, the error catalog, and the CHG
        template enums."""
        catalog = (GOVERNANCE / "chg" / "gates" / "GATE_ERROR_CATALOG.md").read_text(
            encoding="utf-8"
        )
        for code in ("GATE-SPEC-E001", "GATE-SPEC-E002", "GATE-SPEC-E003", "GATE-SPEC-E004"):
            self.assertIn(code, catalog, f"error catalog missing {code}")

        template = (GOVERNANCE / "chg" / "CHG-TEMPLATE.yaml").read_text(encoding="utf-8")
        self.assertIn("GATE-SPEC", template, "CHG-TEMPLATE does not mention GATE-SPEC")
        self.assertIn("spec", template, "CHG-TEMPLATE does not declare the 'spec' change_source")
        self.assertIn("semver_impact", template, "CHG-TEMPLATE missing semver_impact field")

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
            mandatory | skippable,
            set(ARTIFACTS),
            "adaptation layer split references an unknown artifact",
        )


class GovernanceFilesNoOrphans(unittest.TestCase):
    """Any new file under framework/governance/ must be added to EXPECTED_FILES."""

    def test_no_orphan_governance_files(self):
        actual = {p.name for p in GOVERNANCE.iterdir() if p.is_file()}
        expected = set(EXPECTED_FILES)
        new_in_dir = actual - expected
        self.assertFalse(
            new_in_dir,
            "Governance file(s) on disk but not in EXPECTED_FILES: "
            f"{sorted(new_in_dir)}. Add them to the list (and document in CHANGELOG).",
        )


if __name__ == "__main__":
    unittest.main()
