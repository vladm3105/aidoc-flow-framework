"""Conformance: a platform's skills declare only adaptation knobs that exist
in the closed surface (``ADAPTATION_SURFACE.yaml``), and any skill that declares
``adapts:`` references the adaptation authority in its body (ADAPT-A)."""

import unittest

import yaml

from _spec import FRAMEWORK, PLATFORMS_ROOT

SURFACE = FRAMEWORK / "governance" / "ADAPTATION_SURFACE.yaml"
PLUGIN_SKILLS = PLATFORMS_ROOT / "claude-code-plugin" / "skills"


def surface_knob_names():
    data = yaml.safe_load(SURFACE.read_text(encoding="utf-8"))
    return {knob["name"] for knob in data["knobs"]}


def split_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    return (yaml.safe_load(parts[1]) or {}), parts[2]


def declared_adapts(frontmatter):
    custom = (frontmatter.get("metadata") or {}).get("custom_fields") or {}
    return custom.get("adapts") or []


class AdaptationSurfaceConformance(unittest.TestCase):
    def setUp(self):
        if not PLUGIN_SKILLS.exists():
            self.skipTest("plugin skills absent")
        self.knobs = surface_knob_names()

    def test_declared_adapts_are_in_surface(self):
        violations = []
        for skill in sorted(PLUGIN_SKILLS.glob("*/SKILL.md")):
            frontmatter, _ = split_frontmatter(skill)
            for knob in declared_adapts(frontmatter):
                if knob not in self.knobs:
                    violations.append(f"{skill.parent.name}: {knob!r}")
        self.assertEqual(violations, [], f"out-of-surface adapts knobs: {violations}")

    def test_skills_declaring_adapts_reference_authority(self):
        violations = []
        for skill in sorted(PLUGIN_SKILLS.glob("*/SKILL.md")):
            frontmatter, body = split_frontmatter(skill)
            if declared_adapts(frontmatter) and "ADAPTATION.md" not in body:
                violations.append(skill.parent.name)
        self.assertEqual(violations, [], f"adapts without authority ref: {violations}")

    def test_adapting_set_is_wired(self):
        wired = [
            skill.parent.name
            for skill in PLUGIN_SKILLS.glob("*/SKILL.md")
            if declared_adapts(split_frontmatter(skill)[0])
        ]
        self.assertGreaterEqual(
            len(wired), 35, f"expected >=35 skills wired with adapts, got {len(wired)}"
        )


if __name__ == "__main__":
    unittest.main()
