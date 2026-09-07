"""Conformance: project profiles (``.aidoc/profile.yaml``) carry only
keys that exist in the closed adaptation surface
(``framework/governance/ADAPTATION_SURFACE.yaml``), plus a small set of
allowed top-level metadata keys. The new ``PROFILE-TEMPLATE.yaml``
ships as the bootstrap skeleton — it must parse cleanly and contain
no hard-coded overrides (all knobs commented out).

PROFILE-DELTA-001 v0.4.2.
"""

import unittest

import yaml
from _spec import FRAMEWORK, REPO_ROOT

SURFACE = FRAMEWORK / "governance" / "ADAPTATION_SURFACE.yaml"
TEMPLATE = FRAMEWORK / "governance" / "PROFILE-TEMPLATE.yaml"
EXAMPLES_ROOT = REPO_ROOT / "examples"

# Allowed top-level keys in a project profile. Knob names come from the
# closed surface; the other keys are metadata-only and engine-ignored
# (carried through for human readability).
METADATA_KEYS = {"metadata"}


def surface_knob_names():
    data = yaml.safe_load(SURFACE.read_text(encoding="utf-8"))
    return {knob["name"] for knob in data["knobs"]}


def load_profile(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


class ProfileTemplateConformance(unittest.TestCase):
    """The bootstrap template ships in the framework spec."""

    def test_template_exists(self):
        self.assertTrue(
            TEMPLATE.exists(),
            f"PROFILE-TEMPLATE.yaml missing at {TEMPLATE}",
        )

    def test_template_parses(self):
        # Must be valid YAML even though most content is commented.
        loaded = load_profile(TEMPLATE)
        self.assertIsInstance(loaded, dict)
        self.assertIn("metadata", loaded)

    def test_template_carries_no_hard_overrides(self):
        """The template is a skeleton — knob keys must NOT appear as
        active YAML keys (only as commented-out illustrative blocks)."""
        loaded = load_profile(TEMPLATE)
        knobs = surface_knob_names()
        active_overrides = set(loaded.keys()) & knobs
        self.assertFalse(
            active_overrides,
            f"PROFILE-TEMPLATE.yaml ships with active overrides "
            f"(keys must be commented out): {sorted(active_overrides)}",
        )


class ProjectProfileConformance(unittest.TestCase):
    """Every committed ``.aidoc/profile.yaml`` under ``examples/*/`` honours
    the closed-surface contract."""

    def setUp(self):
        if not EXAMPLES_ROOT.exists():
            self.skipTest("no examples directory")
        self.knobs = surface_knob_names()
        self.allowed = METADATA_KEYS | self.knobs

    def _profiles(self):
        return sorted(EXAMPLES_ROOT.glob("*/.aidoc/profile.yaml"))

    def test_profiles_parse(self):
        profiles = self._profiles()
        if not profiles:
            self.skipTest("no project profiles under examples/")
        for path in profiles:
            with self.subTest(profile=str(path.relative_to(REPO_ROOT))):
                loaded = load_profile(path)
                self.assertIsInstance(
                    loaded,
                    dict,
                    f"profile must parse as a YAML mapping: {path}",
                )

    def test_profiles_only_use_surface_or_metadata_keys(self):
        """Top-level keys must be either metadata or a declared knob from
        the closed adaptation surface. Anything else would be silently
        ignored by a conforming engine (per ADAPTATION_SURFACE.yaml
        closed-knob rule) and is therefore an authoring mistake."""
        profiles = self._profiles()
        if not profiles:
            self.skipTest("no project profiles under examples/")
        for path in profiles:
            with self.subTest(profile=str(path.relative_to(REPO_ROOT))):
                loaded = load_profile(path)
                top_level = set(loaded.keys())
                out_of_surface = top_level - self.allowed
                self.assertFalse(
                    out_of_surface,
                    f"{path.relative_to(REPO_ROOT)}: top-level keys "
                    f"outside the closed adaptation surface — would be "
                    f"silently ignored by a conforming engine: "
                    f"{sorted(out_of_surface)}",
                )


if __name__ == "__main__":
    unittest.main()
