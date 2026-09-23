"""Conformance: 10_EVAL (authoring) vs 10_IPVERIFY (execution) split (#672).

Canon (CHG-08): authoring lives in `playbooks/10_EVAL/`; cycle execution and
RPT reports live in `playbooks/10_IPVERIFY/`. Every 10_IPVERIFY playbook
drives the EVAL-RPT flow (`layer: 10_EVAL`), and the README table lists all
four playbooks.
"""

import unittest

from _spec import FRAMEWORK

EVAL_PB = FRAMEWORK / "playbooks" / "10_EVAL"
VERIFY_PB = FRAMEWORK / "playbooks" / "10_IPVERIFY"
PLAYBOOKS = ("evaluator.md", "validator.md", "verifier.md", "report_generator.md")


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path.name}: no frontmatter"
    return text.split("---\n", 2)[1]


class PlaybookSplitTests(unittest.TestCase):
    def test_ipverify_playbooks_drive_eval_rpt(self):
        """Every 10_IPVERIFY playbook declares layer 10_EVAL (no 08_IPLAN)."""
        for name in PLAYBOOKS:
            with self.subTest(playbook=name):
                fm = _frontmatter(VERIFY_PB / name)
                self.assertIn("layer: 10_EVAL", fm, f"{name}: wrong layer")
                self.assertNotIn("08_IPLAN", fm, f"{name}: stale layer")

    def test_readme_lists_all_four(self):
        """The README table names all four playbooks (was 3 of 4)."""
        text = (VERIFY_PB / "README.md").read_text(encoding="utf-8")
        for name in PLAYBOOKS:
            self.assertIn(f"`{name}`", text, f"README omits {name}")

    def test_split_canon_stated_both_sides(self):
        """Both READMEs name the authoring/execution split."""
        eval_text = (EVAL_PB / "README.md").read_text(encoding="utf-8")
        verify_text = (VERIFY_PB / "README.md").read_text(encoding="utf-8")
        self.assertIn("10_IPVERIFY", eval_text)
        self.assertIn("10_EVAL", verify_text)

    def test_no_verify_template_flow_in_ipverify(self):
        """No 10_IPVERIFY playbook authors from the superseded VERIFY template."""
        bad = []
        for name in PLAYBOOKS:
            text = (VERIFY_PB / name).read_text(encoding="utf-8")
            if "IPLAN-VERIFY-TEMPLATE.yaml as base" in text:
                bad.append(name)
        self.assertEqual(bad, [], f"still driving VERIFY flow: {bad}")


if __name__ == "__main__":
    unittest.main()
