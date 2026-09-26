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
LAYER_GATES = FRAMEWORK / "layers" / "09_CHG" / "gates"
GOV_GATES = FRAMEWORK / "governance" / "chg" / "gates"
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
        status_rows = [line for line in text.splitlines() if line.startswith("| Status |")]
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

    def test_template_copies_identical(self):
        """The CHG template fork is closed: both copies byte-identical (#667)."""
        self.assertEqual(
            _text(LAYER_TEMPLATE),
            _text(GOV_TEMPLATE),
            "CHG-TEMPLATE.yaml copies diverged — sync from the governance canon",
        )

    def test_gate_copies_identical(self):
        """The 8 mirrored gate files stay byte-identical (#700).

        The #724 drive-by diverged GATE-08 silently because nothing pinned the
        gate twins — only the template. Both mirrors sit three levels under
        framework/, so links authored up-three-then-down resolve in both.
        """
        gov_files = sorted(p.name for p in GOV_GATES.glob("*.md"))
        layer_files = sorted(p.name for p in LAYER_GATES.glob("*.md"))
        self.assertEqual(gov_files, layer_files, "gate mirror file sets differ")
        for name in gov_files:
            with self.subTest(gate=name):
                self.assertEqual(
                    _text(GOV_GATES / name),
                    _text(LAYER_GATES / name),
                    f"{name} copies diverged — sync from the governance canon",
                )

    def test_canon_home_declared(self):
        """Both copies name the governance home as canon on conflict (#667)."""
        for template in (LAYER_TEMPLATE, GOV_TEMPLATE):
            with self.subTest(template=str(template)):
                self.assertIn("Canonical home", _text(template))


class ModulesFirstAgreement(unittest.TestCase):
    def test_flows_doc_has_phases(self):
        """F3 carries Phase 0a/0b plus the review checkpoint (CHG-10)."""
        text = _text(FLOWS)
        for token in ("Phase 0a", "Phase 0b", "Phase 0c", "Review checkpoint"):
            self.assertIn(token, text)

    def test_kernel_f3_row_is_modules_first(self):
        """The §3.1.3 kernel F3 row carries the modules-first note."""
        self.assertIn("modules-first", _text(CORE))

    def test_templates_carry_f3_sections(self):
        """Both template copies carry §4A/§4B, F3-gated (CHG-10)."""
        for template in (LAYER_TEMPLATE, GOV_TEMPLATE):
            with self.subTest(template=str(template)):
                text = _text(template)
                self.assertIn("module_lifecycle:", text)
                self.assertIn("seed_scope:", text)
                self.assertIn("F3", text)

    def test_readmes_point_at_phases(self):
        """Both 09_CHG READMEs point Phase 0 at the modules-first flow."""
        for readme in (LAYER_README, GOV_README):
            with self.subTest(readme=str(readme)):
                text = _text(readme)
                self.assertIn("modules-first", text)
                self.assertIn("CHG_REQUEST_FLOWS.md", text)

    def test_gov020_catalogued_and_emitted(self):
        """GOV-020 is catalogued and the linter emits CHG-L014 (codes-vs-catalog)."""
        self.assertIn("`GOV-020`", _text(LINT_RULES))
        self.assertIn("CHG-L014", _text(CHG_LINT))
        self.assertIn("GOV-020", _text(CHG_LINT))


class SeedVersioningAgreement(unittest.TestCase):
    def test_flows_doc_has_supersede(self):
        """F3 Phase 0a names the supersede decision + ledger re-point (CHG-11)."""
        text = _text(FLOWS)
        for token in ("supersede", "seed_version", "Review checkpoint"):
            self.assertIn(token, text)

    def test_kernel_f3_row_is_seed_versioned(self):
        """The §3.1.3 kernel F3 row carries the seed-versioning note."""
        self.assertIn("supersede-capable", _text(CORE))

    def test_templates_carry_supersede_entries(self):
        """Both template copies carry the supersede enum + entries + attribution (CHG-11)."""
        for template in (LAYER_TEMPLATE, GOV_TEMPLATE):
            with self.subTest(template=str(template)):
                text = _text(template)
                self.assertIn("no-change | supersede | create", text)
                self.assertIn("entries:", text)
                self.assertIn("chg_ref", text)

    def test_readmes_point_at_supersede(self):
        """Both 09_CHG READMEs point Phase 0 at the supersede-capable flow."""
        for readme in (LAYER_README, GOV_README):
            with self.subTest(readme=str(readme)):
                text = _text(readme)
                self.assertIn("supersede", text)
                self.assertIn("CHG_REQUEST_FLOWS.md", text)

    def test_gov021_catalogued_and_emitted(self):
        """GOV-021 is catalogued and the linter emits CHG-L015 (codes-vs-catalog)."""
        self.assertIn("`GOV-021`", _text(LINT_RULES))
        self.assertIn("CHG-L015", _text(CHG_LINT))
        self.assertIn("GOV-021", _text(CHG_LINT))


if __name__ == "__main__":
    unittest.main()
