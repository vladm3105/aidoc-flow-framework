"""Conformance: 10_EVAL (authoring) vs 10_IPVERIFY (execution) split (#672).

Canon (CHG-08): authoring lives in `playbooks/10_EVAL/`; cycle execution and
RPT reports live in `playbooks/10_IPVERIFY/`. Every 10_IPVERIFY playbook
drives the EVAL-RPT flow (`layer: 10_EVAL`), and the README table lists all
four playbooks.
"""

import re
import unittest

import yaml
from _spec import FRAMEWORK

EVAL_PB = FRAMEWORK / "playbooks" / "10_EVAL"
VERIFY_PB = FRAMEWORK / "playbooks" / "10_IPVERIFY"
PLAYBOOKS = ("evaluator.md", "validator.md", "verifier.md", "report_generator.md")
RPT_TEMPLATE = FRAMEWORK / "layers" / "10_EVAL" / "EVAL-REPORT-TEMPLATE.yaml"


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

    def test_validator_example_uses_template_keys(self):
        """validator.md's Output Example uses only EVAL-REPORT-TEMPLATE keys (#709).

        The example once showed `validation_summary:` / `recommendations:` /
        `p3_count:` — a shape no template or consumer recognizes.
        """
        text = (VERIFY_PB / "validator.md").read_text(encoding="utf-8")
        section = text.split("## Output Example", 1)[1]
        fence = re.search(r"```yaml\n(.*?)```", section, re.DOTALL)
        self.assertIsNotNone(fence, "validator.md has no yaml Output Example")
        example = yaml.safe_load(fence.group(1))
        # The template must itself parse (see #753) — an unparseable
        # template errors here rather than passing silently.
        template = yaml.safe_load(RPT_TEMPLATE.read_text(encoding="utf-8"))
        template_keys = set(template)
        self.assertTrue(template_keys, "no top-level keys found in template")
        self.assertTrue(
            set(example) <= template_keys,
            f"example keys not in template: {sorted(set(example) - template_keys)}",
        )
        self.assertNotIn("p3", fence.group(1), "example invents a P3 severity")


if __name__ == "__main__":
    unittest.main()
