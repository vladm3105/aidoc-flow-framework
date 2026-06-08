"""Synthesizer discards findings without a check citation or with fabricated check ids."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "platforms" / "claude-code-plugin" / "tools"))


class FindingFilterTests(unittest.TestCase):
    def _filter(self, findings, valid_checks):
        from finding_filter import filter_findings

        return filter_findings(findings, valid_check_ids=valid_checks)

    def test_finding_with_valid_check_id_is_kept(self):
        kept, discarded = self._filter(
            findings=[{"id": "CE-1", "priority": "P2", "check": "C1"}],
            valid_checks={"C1", "C2"},
        )
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(discarded), 0)

    def test_finding_without_check_field_is_discarded(self):
        kept, discarded = self._filter(
            findings=[{"id": "CE-1", "priority": "P2"}],  # no 'check' field
            valid_checks={"C1", "C2"},
        )
        self.assertEqual(len(kept), 0)
        self.assertEqual(len(discarded), 1)
        self.assertEqual(discarded[0]["reason"], "no_check_citation")

    def test_finding_with_fabricated_check_id_is_discarded(self):
        kept, discarded = self._filter(
            findings=[{"id": "CE-1", "priority": "P2", "check": "C99"}],
            valid_checks={"C1", "C2"},
        )
        self.assertEqual(len(kept), 0)
        self.assertEqual(len(discarded), 1)
        self.assertEqual(discarded[0]["reason"], "unknown_check")
        self.assertEqual(discarded[0]["check"], "C99")

    def test_beyond_checklist_finding_is_kept(self):
        kept, discarded = self._filter(
            findings=[
                {
                    "id": "CE-2",
                    "priority": "P2",
                    "check": "beyond-checklist:degraded-mode-asymmetry",
                }
            ],
            valid_checks={"C1", "C2"},
        )
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(discarded), 0)


class CoverageEmissionTests(unittest.TestCase):
    def test_coverage_groups_findings_by_check(self):
        from finding_filter import emit_coverage

        findings = [
            {"check": "C1"},
            {"check": "C1"},
            {"check": "C2"},
            {"check": "beyond-checklist:foo"},
            {"check": "beyond-checklist:bar"},
        ]
        coverage = emit_coverage(findings)
        self.assertEqual(coverage["C1"], 2)
        self.assertEqual(coverage["C2"], 1)
        self.assertEqual(coverage["beyond_checklist"], 2)


if __name__ == "__main__":
    unittest.main()
