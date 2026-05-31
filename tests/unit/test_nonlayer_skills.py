"""Unit: non-layer skills (charts-flow, doc-ref, project-init, doc-flow)."""

import re
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root

SKILLS_DIR = plugin_bundle_root() / "skills"
NON_LAYER_SKILLS = ["charts-flow", "doc-ref", "project-init", "doc-flow"]


def frontmatter(skill_dir: Path) -> dict:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return yaml.safe_load(match.group(1)) if match else {}


class NonLayerSkillContractTests(unittest.TestCase):
    def test_each_non_layer_skill_exists_or_is_acceptably_absent(self):
        missing = [
            name for name in NON_LAYER_SKILLS if not (SKILLS_DIR / name / "SKILL.md").exists()
        ]
        self.assertLessEqual(
            len(missing),
            2,
            f"More than 2 non-layer skills missing: {missing}",
        )

    def test_each_present_non_layer_skill_carries_skill_category(self):
        for name in NON_LAYER_SKILLS:
            skill_dir = SKILLS_DIR / name
            if not (skill_dir / "SKILL.md").exists():
                continue
            with self.subTest(skill=name):
                fm = frontmatter(skill_dir)
                category = fm.get("metadata", {}).get("custom_fields", {}).get("skill_category")
                self.assertIsNotNone(category, f"{name}: missing skill_category")
