"""Unit test for sdd_doc_lint. Run with `tools/` on the path:

PYTHONPATH=tools python3 -m unittest discover -s tools/sdd_doc_lint/tests
"""

import unittest
from pathlib import Path

from sdd_doc_lint import lint_path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class DocLint(unittest.TestCase):
    def test_valid_fixtures_have_no_findings(self):
        findings = lint_path(FIXTURES / "valid")
        self.assertEqual([str(f) for f in findings], [], "valid fixtures should be clean")

    def test_broken_fixtures_trip_each_check(self):
        findings = lint_path(FIXTURES / "broken")
        codes = {f.code for f in findings}
        for expected in (
            "TAG01",
            "PH01",
            "ID01",
            "ID02",
            "ID03",
            "EARS01",
            "TH01",
            "STY01",
            "STY02",
            "TH02",
            "FM01",
            "DG02",
            "HASH01",
            "CSC01",
        ):
            self.assertIn(
                expected, codes, f"broken fixtures should trip {expected}; got {sorted(codes)}"
            )

    def test_style_findings_are_warnings_by_default(self):
        """STY01 (banned phrase) and STY02 (oversized section) are warnings —
        they do not flip lint to non-zero exit on their own."""
        findings = lint_path(FIXTURES / "broken")
        for f in findings:
            if f.code in ("STY01", "STY02"):
                self.assertEqual(
                    f.severity,
                    "warning",
                    f"{f.code} should be advisory; got severity={f.severity}",
                )

    def test_non_sdd_file_is_ignored(self):
        # A file the path/name doesn't classify as an SDD instance doc → no findings.
        findings = lint_path(Path(__file__))
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
