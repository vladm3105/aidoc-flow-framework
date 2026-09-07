"""Conformance: every layer autopilot drives the saga driver (SAGA-PARITY-001
Phase 4).

Each ``doc-<layer>-autopilot`` SKILL must, in ``review_mode: team`` (the
framework default), invoke the preemptive ``saga_driver.py`` rather than draft
in-session. This guards against the divergence where the acceptance harness
shells the driver directly while the autopilot SKILL still describes a legacy
in-session loop. Every layer autopilot must therefore:

  * carry the ``### Saga-driven generation loop`` subsection,
  * invoke ``saga_driver.py --layer <NN_TYPE>`` with the correct layer arg,
  * retain the ``### Linear Pipeline`` (``single_pass``) fallback subsection,
  * declare ``review_mode`` in its ``adapts:`` frontmatter (it branches on it).
"""

import unittest

import yaml
from _spec import PLATFORMS_ROOT

PLUGIN_SKILLS = PLATFORMS_ROOT / "claude-code-plugin" / "skills"

# layer autopilot -> the --layer NN_TYPE arg the saga driver expects
LAYER_AUTOPILOTS = {
    "doc-brd-autopilot": "01_BRD",
    "doc-prd-autopilot": "02_PRD",
    "doc-ears-autopilot": "03_EARS",
    "doc-bdd-autopilot": "04_BDD",
    "doc-adr-autopilot": "05_ADR",
    "doc-spec-autopilot": "06_SPEC",
    "doc-tdd-autopilot": "07_TDD",
    "doc-iplan-autopilot": "08_IPLAN",
}

# Every SKILL that shells the driver, including the CHG autopilot, which is
# outside the 8-layer flow above but invokes the driver identically.
DRIVER_INVOKERS = dict(LAYER_AUTOPILOTS, **{"doc-chg-autopilot": "09_CHG"})


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


class AutopilotSagaParity(unittest.TestCase):
    def setUp(self):
        if not PLUGIN_SKILLS.exists():
            self.skipTest("plugin skills absent")

    def _skill(self, name):
        path = PLUGIN_SKILLS / name / "SKILL.md"
        self.assertTrue(path.exists(), f"{name}/SKILL.md missing")
        return path

    def test_team_saga_block_present(self):
        for name, layer in LAYER_AUTOPILOTS.items():
            with self.subTest(skill=name):
                _, body = split_frontmatter(self._skill(name))
                self.assertIn(
                    "### Saga-driven generation loop",
                    body,
                    f"{name}: missing team-mode saga subsection",
                )
                self.assertIn(
                    "saga_driver.py",
                    body,
                    f"{name}: missing saga_driver.py invocation",
                )
                self.assertIn(
                    f"--layer {layer}",
                    body,
                    f"{name}: missing/incorrect '--layer {layer}'",
                )

    def test_single_pass_fallback_retained(self):
        for name in LAYER_AUTOPILOTS:
            with self.subTest(skill=name):
                _, body = split_frontmatter(self._skill(name))
                self.assertIn(
                    "### Linear Pipeline",
                    body,
                    f"{name}: missing single_pass linear-pipeline fallback",
                )

    def test_review_mode_declared_in_adapts(self):
        for name in LAYER_AUTOPILOTS:
            with self.subTest(skill=name):
                fm, _ = split_frontmatter(self._skill(name))
                self.assertIn(
                    "review_mode",
                    declared_adapts(fm),
                    f"{name}: adapts must declare review_mode (it branches on it)",
                )

    def test_driver_invocation_passes_the_permission_flag(self):
        """PLUGIN-PREPROD-001 B2: the permission bypass is opt-in in the
        driver, so every invoker must *pass* `--allow-skip-permissions`, not
        merely mention it. A documentation-only change would strip the bypass
        from the plugin's primary path and from the live cascade.

        Asserted on the invocation block itself — prose elsewhere in the SKILL
        naming the flag is not a passed argument.
        """
        for name in DRIVER_INVOKERS:
            with self.subTest(skill=name):
                _, body = split_frontmatter(self._skill(name))
                blocks = [b for b in body.split("```") if "saga_driver.py" in b and "python3" in b]
                self.assertTrue(blocks, f"{name}: no saga_driver.py invocation block")
                for block in blocks:
                    self.assertIn(
                        "--allow-skip-permissions",
                        block,
                        f"{name}: driver invocation does not pass --allow-skip-permissions",
                    )

    def test_no_dangling_singlepass_crossref(self):
        # Regression guard (Phase 4 review): the team-mode saga block must state
        # the index/downstream update directly, not forward-reference a
        # single_pass step that does not describe it.
        for name in LAYER_AUTOPILOTS:
            with self.subTest(skill=name):
                _, body = split_frontmatter(self._skill(name))
                self.assertNotIn(
                    "per the single_pass step below",
                    body,
                    f"{name}: dangling forward-reference to single_pass in the saga block",
                )


if __name__ == "__main__":
    unittest.main()
