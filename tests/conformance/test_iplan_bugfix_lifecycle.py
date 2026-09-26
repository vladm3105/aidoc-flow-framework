"""Conformance: IPLAN post-completion defect repair vehicle (CHG-05, #656/#657).

Test-first contract for the scoped bugfix IPLAN subtype and its lifecycle
prose. Written RED before the template/index/README/VERIFY edits (plan Task
2) and the linter + catalog rows (plan Task 4); goes green incrementally as
each lands. Nothing here weakens an existing guard.
"""

import re
import unittest
from pathlib import Path

import yaml
from _spec import FRAMEWORK, REPO_ROOT

IPLAN_DIR = FRAMEWORK / "layers" / "08_IPLAN"
TEMPLATE = IPLAN_DIR / "IPLAN-TEMPLATE.yaml"
README = IPLAN_DIR / "README.md"
VERIFY_TEMPLATE = IPLAN_DIR / "IPLAN-VERIFY-TEMPLATE.yaml"
CORE = FRAMEWORK / "governance" / "DOC_GOVERNANCE_CORE.md"
INDEX_TEMPLATE = IPLAN_DIR / "IPLAN-00_index.TEMPLATE.yaml"
LINT_RULES = FRAMEWORK / "governance" / "LINT_RULES.md"
BUGFIX_LINT = REPO_ROOT / "sdd_doc_lint" / "bugfix_lint.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TemplateBugfixSubtype(unittest.TestCase):
    def test_subtype_enum_includes_bugfix(self):
        """The subtype enum carries bugfix without removing the combined default."""
        text = _text(TEMPLATE)
        self.assertIn("bugfix", text, "IPLAN-TEMPLATE.yaml names no bugfix subtype")
        self.assertIn("combined", text, "combined default must survive the addition")

    def test_parent_and_source_homes(self):
        """The template declares parent_iplan + source_chg homes for the vehicle."""
        text = _text(TEMPLATE)
        self.assertIn("parent_iplan", text, "no parent_iplan home in IPLAN-TEMPLATE.yaml")
        self.assertIn("source_chg", text, "no source_chg home in IPLAN-TEMPLATE.yaml")

    def test_step_order_and_rollback_guidance(self):
        """Normative order (fix → regression → rollback → revision entry last)
        and PENDING→DONE/SKIPPED rollback markers are prescribed in-template."""
        text = _text(TEMPLATE)
        self.assertRegex(
            text,
            re.compile(r"fix.*regression.*rollback.*revision", re.DOTALL | re.IGNORECASE),
            "no normative bugfix step order in IPLAN-TEMPLATE.yaml",
        )
        self.assertIn("PENDING", text, "no PENDING rollback marker in IPLAN-TEMPLATE.yaml")

    def test_template_still_parses(self):
        """The edited template remains valid YAML with an iplan-document core."""
        doc = yaml.safe_load(_text(TEMPLATE))
        self.assertIsInstance(doc, dict)
        self.assertEqual(doc.get("doc_id"), "IPLAN-NN")
        self.assertIn("document_control", doc)
        self.assertIn("file_manifest", doc)


class ReadmeLifecycle(unittest.TestCase):
    def test_completed_validatable_verified_terminal(self):
        """Completed awaits validation; Verified alone is terminal/immutable."""
        text = _text(README)
        self.assertIn("Completed", text)
        self.assertIn("Verified", text)
        self.assertIn("immutable", text.lower())

    def test_bugfix_routing(self):
        """README routes post-completion repair to the bugfix vehicle and
        defines which statuses count as active for the §3.13 exception."""
        text = _text(README)
        self.assertIn("bugfix", text.lower(), "no bugfix routing in 08_IPLAN/README.md")
        self.assertIn("active", text.lower(), "no active-IPLAN definition pointer in README")


class IndexTemplate(unittest.TestCase):
    def test_pending_validated_by_and_parent_linkage(self):
        """The index template supports a pending VERIFY obligation for
        merged-at-Completed plans plus bugfix-parent linkage."""
        text = _text(INDEX_TEMPLATE)
        self.assertIn("validated_by", text)
        self.assertIn("pending", text.lower())
        self.assertIn("parent", text.lower(), "no bugfix-parent linkage in index template")


class VerifyTemplate(unittest.TestCase):
    def test_dry_run_requirement(self):
        """Migration verification requires fresh-rebuild + live-DB dry-run,
        not fmt/lint alone. Canonical home is the Migration VERIFY rule in
        DOC_GOVERNANCE_CORE.md since IPLAN-VERIFY-TEMPLATE.yaml was
        tombstoned (#698) — the retired template no longer carries requirements."""
        text = _text(CORE)
        self.assertIn("dry-run", text.lower(), "no dry-run requirement in CORE")


class LintCatalog(unittest.TestCase):
    def test_gov013_carveout_catalogued(self):
        """LINT_RULES carries the GOV-013 carve-out for the bugfix vehicle."""
        catalog = _text(LINT_RULES)
        self.assertIn("GOV-013", catalog)
        self.assertIn("bugfix", catalog.lower(), "no bugfix carve-out in LINT_RULES.md")

    def test_bgf_checks_catalogued(self):
        """Every BGF-NN check the bugfix linter can emit appears in LINT_RULES.md."""
        if not BUGFIX_LINT.is_file():
            self.fail("sdd_doc_lint/bugfix_lint.py not yet implemented (plan Task 4)")
        emitted = sorted(set(re.findall(r"BGF-(\d+)", _text(BUGFIX_LINT))))
        self.assertTrue(emitted, "bugfix linter emits no BGF-NN checks")
        catalog = _text(LINT_RULES)
        for num in emitted:
            with self.subTest(check=f"BGF-{num}"):
                self.assertIn(
                    f"`BGF-{num}`",
                    catalog,
                    f"BGF-{num} emitted by bugfix_lint.py but absent from LINT_RULES.md",
                )


if __name__ == "__main__":
    unittest.main()
