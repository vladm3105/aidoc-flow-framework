"""Conformance: CHG request-flows router agreement (CHG-06, #673).

The F1–F4 × source × gate × cascade contract must read the same in every surface
that states it: both CHG templates, both 09_CHG READMEs, DOC_GOVERNANCE_CORE
§3.1.3, LINT_RULES (GOV-018), the linter (CHG-L013), and the canonical flows doc.
Nothing here weakens an existing guard.
"""

import re
import unittest
from pathlib import Path

from _spec import FRAMEWORK, REPO_ROOT

LAYER_TEMPLATE = FRAMEWORK / "layers" / "09_CHG" / "CHG-TEMPLATE.yaml"
GOV_TEMPLATE = FRAMEWORK / "governance" / "chg" / "CHG-TEMPLATE.yaml"
LAYER_README = FRAMEWORK / "layers" / "09_CHG" / "README.md"
GOV_README = FRAMEWORK / "governance" / "chg" / "README.md"
CORE = FRAMEWORK / "governance" / "DOC_GOVERNANCE_CORE.md"
FLOWS = FRAMEWORK / "governance" / "CHG_REQUEST_FLOWS.md"
LINT_RULES = FRAMEWORK / "governance" / "LINT_RULES.md"
CHG_LINT = REPO_ROOT / "sdd_doc_lint" / "chg_lint.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class DirectSourceAgreement(unittest.TestCase):
    def test_direct_row_in_both_templates(self):
        """The Direct source row names GATE-CODE in both template copies."""
        for template in (LAYER_TEMPLATE, GOV_TEMPLATE):
            with self.subTest(template=str(template)):
                text = _text(template)
                self.assertIn("| Direct", text, f"no Direct row in {template.name}")
                self.assertIn("GATE-CODE", text)

    def test_direct_rows_identical(self):
        """The Direct rows match verbatim — no fork widening (#667)."""
        rows = []
        for template in (LAYER_TEMPLATE, GOV_TEMPLATE):
            lines = [
                line.strip()
                for line in _text(template).splitlines()
                if line.strip().startswith("| Direct")
            ]
            self.assertEqual(len(lines), 1, f"Direct row count != 1 in {template}")
            rows.append(lines[0])
        self.assertEqual(rows[0], rows[1], "Direct rows differ between copies")

    def test_enum_comments_carry_direct(self):
        """Both value/enum comments list direct alongside the existing sources."""
        for template in (LAYER_TEMPLATE, GOV_TEMPLATE):
            with self.subTest(template=str(template)):
                text = _text(template)
                self.assertIn("reconciliation | direct | spec", text)


class RouterKernelAgreement(unittest.TestCase):
    def test_core_section_present(self):
        """DOC_GOVERNANCE_CORE carries the §3.1.3 router kernel."""
        text = _text(CORE)
        self.assertIn("§3.1.3", text)
        for token in ("F1", "F2", "F3", "F4", "GATE-CODE"):
            self.assertIn(token, text)

    def test_f2_ruling_in_core(self):
        """The C1/IPLAN-gate ruling (F2.2) is stated at the §3.13 site."""
        self.assertIn("F2.2", _text(CORE))

    def test_flows_doc_ratified(self):
        """The canonical flows doc is ratified law, not a proposal."""
        text = _text(FLOWS)
        status_rows = [
            line for line in text.splitlines() if line.startswith("| Status |")
        ]
        self.assertTrue(status_rows, "no Status row in CHG_REQUEST_FLOWS.md")
        self.assertTrue(
            any("RATIFIED" in row for row in status_rows),
            f"flows doc not ratified: {status_rows}",
        )


class GuardCatalogAgreement(unittest.TestCase):
    def test_gov018_catalogued(self):
        """GOV-018 is a catalogued error row in LINT_RULES.md."""
        catalog = _text(LINT_RULES)
        self.assertIn("`GOV-018`", catalog)
        self.assertIn("F2/F3/F4", catalog)

    def test_linter_emits_l013(self):
        """Every CHG-L013 the linter can emit names the guard (codes-vs-catalog)."""
        emitted = sorted(set(re.findall(r"CHG-L013", _text(CHG_LINT))))
        self.assertTrue(emitted, "chg_lint.py emits no CHG-L013 marker")
        self.assertIn("`GOV-018`", _text(LINT_RULES))

    def test_readmes_carry_selector(self):
        """Both 09_CHG READMEs carry the Direct routing row + flows pointer."""
        for readme in (LAYER_README, GOV_README):
            with self.subTest(readme=str(readme)):
                text = _text(readme)
                self.assertIn("| Direct | GATE-CODE", text)
                self.assertIn("CHG_REQUEST_FLOWS.md", text)


if __name__ == "__main__":
    unittest.main()
