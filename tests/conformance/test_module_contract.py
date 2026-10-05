"""Conformance test for MODULE-TEMPLATE.md and SEED_TO_MODULE_DECOMPOSITION.md (GD-50).

Asserts existence, frontmatter schema, diagram tags, and governance reconciliation.
"""

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRAMEWORK = REPO_ROOT / "framework"


class ModuleTemplateContract(unittest.TestCase):
    """GD-50: canonical MODULE-TEMPLATE.md existence, frontmatter schema, and guidance."""

    def setUp(self):
        self.template_path = FRAMEWORK / "templates" / "MODULE-TEMPLATE.md"
        self.decomposition_path = FRAMEWORK / "governance" / "SEED_TO_MODULE_DECOMPOSITION.md"
        self.seed_template_path = FRAMEWORK / "templates" / "SEED-TEMPLATE.md"

    def test_module_template_exists(self):
        """Canonical MODULE-TEMPLATE.md must exist in framework/templates/."""
        self.assertTrue(self.template_path.is_file(), f"Missing {self.template_path}")

    def test_decomposition_playbook_exists(self):
        """SEED_TO_MODULE_DECOMPOSITION.md must exist in framework/governance/."""
        self.assertTrue(self.decomposition_path.is_file(), f"Missing {self.decomposition_path}")

    def test_module_template_frontmatter(self):
        """Template frontmatter must parse and carry required document_control keys."""
        content = self.template_path.read_text(encoding="utf-8")
        parts = content.split("---")
        self.assertGreaterEqual(len(parts), 3, "MODULE-TEMPLATE.md lacks valid frontmatter block")
        data = yaml.safe_load(parts[1])
        dc = data.get("document_control", {})

        required_keys = [
            "title",
            "version",
            "type",
            "module_id",
            "status",
            "owners",
            "c4_level",
            "data_classification",
            "last_updated",
        ]
        for key in required_keys:
            self.assertIn(key, dc, f"document_control missing required key: {key}")

        self.assertEqual(dc.get("type"), "MODULE")
        self.assertEqual(dc.get("c4_level"), "c4-l2")

    def test_module_template_version_within_regex_limit(self):
        """Line distance between document_control: and version: must be <= 12 lines."""
        lines = self.template_path.read_text(encoding="utf-8").splitlines()
        dc_idx = None
        ver_idx = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("document_control:"):
                dc_idx = i
            elif dc_idx is not None and stripped.startswith("version:"):
                ver_idx = i
                break

        self.assertIsNotNone(dc_idx, "document_control: not found in MODULE-TEMPLATE.md")
        self.assertIsNotNone(ver_idx, "version: not found in MODULE-TEMPLATE.md")
        distance = ver_idx - dc_idx
        self.assertLessEqual(
            distance, 12, f"version: is {distance} lines from document_control: (max 12)"
        )

    def test_module_template_contains_triple_lens_sections(self):
        """Template must contain C4-L2, DFD-L2 with data matrix, and sequence flow."""
        content = self.template_path.read_text(encoding="utf-8")
        self.assertIn("@diagram: c4-l2", content)
        self.assertIn("@diagram: dfd-l2", content)
        self.assertIn("@diagram: sequence-sync", content)
        self.assertIn("Data Sensitivity & Protection Matrix", content)
        self.assertIn("Subsystem Invariants & Constraints", content)

    def test_decomposition_playbook_contains_5_steps(self):
        """Decomposition playbook must detail all 5 methodology steps."""
        content = self.decomposition_path.read_text(encoding="utf-8")
        self.assertIn("Step 1: Domain Boundary Discovery", content)
        self.assertIn("Step 2: Structural Container Modeling", content)
        self.assertIn("Step 3: Data Movement, Trust Boundaries & Sensitivity Mapping", content)
        self.assertIn("Step 4: Inter-Module Process Choreography & Failure Paths", content)
        self.assertIn("Step 5: Integrity, Invariant & Traceability Audit", content)

    def test_seed_template_contains_c4_and_dfd_l1(self):
        """SEED-TEMPLATE.md must contain C4-L1 and DFD-L1 diagrams."""
        content = self.seed_template_path.read_text(encoding="utf-8")
        self.assertIn("@diagram: c4-l1", content)
        self.assertIn("@diagram: dfd-l1", content)

    def test_diagram_standards_records_seed_and_module(self):
        """DIAGRAM_STANDARDS.md must list Seed (C4-L1) and Module (C4-L2, DFD-L2) in ownership model."""
        content = (FRAMEWORK / "governance" / "DIAGRAM_STANDARDS.md").read_text(encoding="utf-8")
        self.assertIn("Seed (Tier 1 Inputs)", content)
        self.assertIn("Module (Tier 2 Domain)", content)
        self.assertIn("C4 L2 (Container) + DFD L2 + sequence", content)

    def test_decisions_records_gd50(self):
        """DECISIONS.md must record GD-50."""
        content = (FRAMEWORK / "governance" / "DECISIONS.md").read_text(encoding="utf-8")
        self.assertIn("GD-50", content, "GD-50 not found in DECISIONS.md")


if __name__ == "__main__":
    unittest.main()
