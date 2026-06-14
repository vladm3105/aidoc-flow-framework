"""Unit tests for `_harness.template_sections()` — the template-side
optional/conditional flag semantics introduced by ACCEPTANCE-FIXTURES-DRIFT.

Two flags are honored:

* ``_required: false`` (PRD ``component_decomposition`` — CLEANUP-PR-D)
* ``_required_when_subtype: [list]`` (IPLAN sub-types — CLEANUP-PR-E item 17)

These tests fix the function's behavior so the per-layer and fullpath
acceptance tests can stop reporting false-positive "missing template
sections" findings.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import template_sections  # noqa: E402


class TemplateSectionsTests(unittest.TestCase):
    def test_prd_excludes_component_decomposition(self):
        """PRD template marks `component_decomposition` with
        `_required: false` (underscore prefix). The function must exclude
        it from the required set — even though `component_decomposition`
        has no plain `required: False` key."""
        sections = template_sections("PRD")
        self.assertNotIn("component_decomposition", sections)

    def test_iplan_combined_includes_deploy_sections(self):
        """IPLAN subtype `combined` requires both code-build and deploy
        sections per the template's `_required_when_subtype:` lists."""
        sections = template_sections("IPLAN", subtype="combined")
        # Code-build sections
        self.assertIn("file_manifest", sections)
        self.assertIn("execution_commands", sections)
        # Deploy sections
        self.assertIn("rollback_procedure", sections)
        self.assertIn("smoke_tests", sections)
        self.assertIn("canary_metrics", sections)
        self.assertIn("observability_hooks", sections)
        self.assertIn("runbook_reference", sections)

    def test_iplan_code_build_excludes_deploy_sections(self):
        """IPLAN subtype `code_build` requires code-build sections only;
        deploy sections are excluded by their `_required_when_subtype:`
        list (which contains `deploy`/`combined` but not `code_build`)."""
        sections = template_sections("IPLAN", subtype="code_build")
        # Code-build sections still present
        self.assertIn("file_manifest", sections)
        self.assertIn("execution_commands", sections)
        # Deploy sections excluded
        self.assertNotIn("rollback_procedure", sections)
        self.assertNotIn("smoke_tests", sections)
        self.assertNotIn("canary_metrics", sections)
        self.assertNotIn("observability_hooks", sections)
        self.assertNotIn("runbook_reference", sections)

    def test_iplan_none_subtype_excludes_gated_sections(self):
        """When `subtype=None` (caller doesn't know), sections gated by
        `_required_when_subtype:` are excluded. Conservative default —
        matches today's behavior for layers whose templates don't use the
        marker (BRD/PRD/EARS/BDD/ADR/SPEC/TDD)."""
        sections = template_sections("IPLAN")
        # All deploy sections excluded since none qualify without subtype
        self.assertNotIn("rollback_procedure", sections)
        # Code-build sections also gated by subtype → excluded
        self.assertNotIn("file_manifest", sections)

    def test_brd_unaffected_by_subtype_parameter(self):
        """BRD template uses no `_required_when_subtype:` markers, so
        the subtype parameter is irrelevant. Both calls return the same
        set."""
        without = template_sections("BRD")
        with_combined = template_sections("BRD", subtype="combined")
        self.assertEqual(set(without), set(with_combined))


if __name__ == "__main__":
    unittest.main()
