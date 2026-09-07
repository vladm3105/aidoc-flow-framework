"""Conformance: every layer autopilot surfaces the per-layer model
recommendation (MODEL-PRECHECK-ROLLOUT).

`commands/model.md` documents that `model.precheck` is consulted by the
drafting skills; this asserts the autopilot entry points actually carry that
`## Model precheck` section, reference the canonical `model.*` config keys, and
place the section BEFORE the saga-driver invocation (so the notice prints in the
live session before the headless cascade starts — not after / not bypassing the
driver).
"""

import unittest

import yaml
from _spec import PLATFORMS_ROOT

PLUGIN_SKILLS = PLATFORMS_ROOT / "claude-code-plugin" / "skills"

LAYER_AUTOPILOTS = [
    "doc-brd-autopilot",
    "doc-prd-autopilot",
    "doc-ears-autopilot",
    "doc-bdd-autopilot",
    "doc-adr-autopilot",
    "doc-spec-autopilot",
    "doc-tdd-autopilot",
    "doc-iplan-autopilot",
]

CONFIG_KEYS = ("model.precheck", "model.per_layer", "model.default")


def split_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    return (yaml.safe_load(parts[1]) or {}), parts[2]


class ModelPrecheckRollout(unittest.TestCase):
    def setUp(self):
        if not PLUGIN_SKILLS.exists():
            self.skipTest("plugin skills absent")

    def _body(self, name):
        path = PLUGIN_SKILLS / name / "SKILL.md"
        self.assertTrue(path.exists(), f"{name}/SKILL.md missing")
        return split_frontmatter(path)[1]

    def test_precheck_section_present_with_keys(self):
        for name in LAYER_AUTOPILOTS:
            with self.subTest(skill=name):
                body = self._body(name)
                self.assertIn(
                    "## Model precheck",
                    body,
                    f"{name}: missing '## Model precheck' section",
                )
                for key in CONFIG_KEYS:
                    self.assertIn(
                        key,
                        body,
                        f"{name}: Model precheck must reference {key}",
                    )

    def test_precheck_precedes_saga_driver(self):
        for name in LAYER_AUTOPILOTS:
            with self.subTest(skill=name):
                body = self._body(name)
                precheck_at = body.find("## Model precheck")
                driver_at = body.find("saga_driver.py")
                self.assertNotEqual(precheck_at, -1, f"{name}: no precheck section")
                self.assertNotEqual(driver_at, -1, f"{name}: no saga_driver.py")
                self.assertLess(
                    precheck_at,
                    driver_at,
                    f"{name}: '## Model precheck' must come BEFORE the saga_driver.py invocation",
                )


if __name__ == "__main__":
    unittest.main()
