"""Unit tests for sdd_doc_lint.surface_lint (rules SURF-001 through SURF-004)."""

import tempfile
import unittest
from pathlib import Path

from sdd_doc_lint.surface_lint import lint_surfaces, main


class TestSurfaceLint(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_repository_has_zero_findings(self):
        findings = lint_surfaces(self.root)
        self.assertEqual(len(findings), 0)

    def test_loose_decisions_emits_surf_001_error(self):
        decisions_file = self.root / "DECISIONS.md"
        decisions_file.write_text(
            "# Active Project Decisions\n\n1. Use Postgres\n", encoding="utf-8"
        )

        findings = lint_surfaces(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SURF-001")
        self.assertEqual(findings[0].severity, "ERROR")
        self.assertIn("docs/sdd/05_ADR/", findings[0].remediation)

    def test_docs_decisions_emits_surf_001_error(self):
        docs_dir = self.root / "docs"
        docs_dir.mkdir()
        (docs_dir / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")

        findings = lint_surfaces(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SURF-001")
        self.assertEqual(findings[0].severity, "ERROR")

    def test_tombstoned_decisions_is_exempt(self):
        decisions_file = self.root / "DECISIONS.md"
        decisions_file.write_text(
            "# Project Decisions (RETIRED / TOMBSTONE)\n\n"
            "This file is FROZEN AS A PERMANENT TOMBSTONE.\n",
            encoding="utf-8",
        )

        findings = lint_surfaces(self.root)
        self.assertEqual(len(findings), 0)

    def test_loose_roadmap_emits_surf_002_warning(self):
        (self.root / "ROADMAP.md").write_text("# Project Roadmap 2026\n", encoding="utf-8")

        findings = lint_surfaces(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SURF-002")
        self.assertEqual(findings[0].severity, "WARNING")
        self.assertIn("plans/*-PLAN.md", findings[0].remediation)

    def test_loose_changelog_emits_surf_003_warning(self):
        (self.root / "CHANGELOG.md").write_text("# Changelog\n\n## v1.0.0\n", encoding="utf-8")

        findings = lint_surfaces(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SURF-003")
        self.assertEqual(findings[0].severity, "WARNING")
        self.assertIn("docs/sdd/09_CHG/archive/", findings[0].remediation)

    def test_tombstoned_changelog_is_exempt(self):
        (self.root / "CHANGELOG.md").write_text(
            "# Changelog (RETIRED / TOMBSTONE)\n\nStatus: Retired / Tombstone\n",
            encoding="utf-8",
        )

        findings = lint_surfaces(self.root)
        self.assertEqual(len(findings), 0)

    def test_loose_handoff_emits_surf_004_error(self):
        docs_dir = self.root / "docs"
        docs_dir.mkdir()
        (docs_dir / "HANDOFF.md").write_text("# Current Session Handoff\n", encoding="utf-8")

        findings = lint_surfaces(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SURF-004")
        self.assertEqual(findings[0].severity, "ERROR")

    def test_main_cli_exit_codes(self):
        # 1. Clean root -> 0
        self.assertEqual(main([str(self.root)]), 0)

        # 2. Warning only (ROADMAP) without --warn-exit -> exits 0
        roadmap = self.root / "ROADMAP.md"
        roadmap.write_text("# Roadmap\n", encoding="utf-8")
        self.assertEqual(main([str(self.root)]), 0)

        # 3. Warning only with --warn-exit -> exits 1
        self.assertEqual(main([str(self.root), "--warn-exit"]), 1)

        # 4. Error (DECISIONS) -> exits 1
        (self.root / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
        self.assertEqual(main([str(self.root)]), 1)


if __name__ == "__main__":
    unittest.main()
