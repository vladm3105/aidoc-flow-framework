"""Unit: every plugin skill carries complete, current frontmatter."""

import re
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK, skill_dirs


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"{skill_md}: missing YAML frontmatter"
    return yaml.safe_load(match.group(1))


REQUIRED_FRONTMATTER_KEYS = {"name", "description", "metadata"}
REQUIRED_CUSTOM_FIELDS = {
    "version",
    "framework_spec_version",
    "last_updated",
    "skill_category",
}


def framework_version() -> str:
    return (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()


def _skill_dirs_with_skill_md() -> list[Path]:
    """Filter skill_dirs() to only directories that actually contain SKILL.md."""
    return [d for d in skill_dirs() if d.is_dir() and (d / "SKILL.md").exists()]


class SkillManifestTests(unittest.TestCase):
    def test_every_skill_has_skill_md(self):
        # Every immediate subdirectory of skills/ must carry a SKILL.md.
        candidates = [d for d in skill_dirs() if d.is_dir()]
        missing = [d for d in candidates if not (d / "SKILL.md").exists()]
        self.assertFalse(missing, f"skills lacking SKILL.md: {[d.name for d in missing]}")

    def test_frontmatter_parses_and_has_required_top_keys(self):
        for skill in _skill_dirs_with_skill_md():
            with self.subTest(skill=skill.name):
                fm = parse_frontmatter(skill / "SKILL.md")
                self.assertGreaterEqual(
                    set(fm),
                    REQUIRED_FRONTMATTER_KEYS,
                    f"{skill.name}: top-level fm missing keys",
                )

    def test_custom_fields_complete(self):
        for skill in _skill_dirs_with_skill_md():
            with self.subTest(skill=skill.name):
                fm = parse_frontmatter(skill / "SKILL.md")
                custom = fm["metadata"].get("custom_fields", {})
                missing = REQUIRED_CUSTOM_FIELDS - set(custom)
                self.assertFalse(missing, f"{skill.name}: missing custom_fields: {missing}")

    def test_framework_spec_version_matches_bundle(self):
        target = framework_version()
        for skill in _skill_dirs_with_skill_md():
            with self.subTest(skill=skill.name):
                fm = parse_frontmatter(skill / "SKILL.md")
                got = fm["metadata"]["custom_fields"]["framework_spec_version"]
                self.assertEqual(
                    got,
                    target,
                    f"{skill.name}: framework_spec_version {got!r} != bundle {target!r}",
                )


if __name__ == "__main__":
    unittest.main()
