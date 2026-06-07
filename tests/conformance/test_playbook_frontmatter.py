"""Every playbook's YAML frontmatter parses + matches REVIEW_CREWS.yaml."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CREWS_PATH = REPO_ROOT / "framework" / "governance" / "REVIEW_CREWS.yaml"
VERSION_PATH = REPO_ROOT / "framework" / "VERSION"
PLAYBOOKS_DIR = REPO_ROOT / "framework" / "playbooks"

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
REQUIRED_FIELDS = {"layer", "lens", "weight", "agent", "framework_spec_version"}


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text()
    m = FM_RE.match(text)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


class PlaybookFrontmatterTests(unittest.TestCase):
    def setUp(self):
        with CREWS_PATH.open() as f:
            self.crews = yaml.safe_load(f)
        self.framework_version = VERSION_PATH.read_text().strip()
        self.playbooks = list(PLAYBOOKS_DIR.rglob("*.md")) if PLAYBOOKS_DIR.exists() else []

    def test_every_playbook_has_required_frontmatter_fields(self):
        for pb in self.playbooks:
            with self.subTest(playbook=str(pb.relative_to(REPO_ROOT))):
                fm = parse_frontmatter(pb)
                self.assertIsNotNone(fm, f"frontmatter missing/malformed in {pb}")
                missing = REQUIRED_FIELDS - set(fm.keys())
                self.assertEqual(missing, set(), f"missing fields: {missing}")

    def test_every_playbook_lens_weight_matches_review_crews(self):
        # crew_lookup[(layer_name, lens)] -> weight
        crew_lookup = {}
        for layer_name, crew in self.crews["crews"].items():
            for lens, weight in crew["review"].items():
                crew_lookup[(layer_name, lens)] = weight

        for pb in self.playbooks:
            fm = parse_frontmatter(pb)
            if fm is None:
                continue
            layer_dir = pb.parent.name  # "02_PRD"
            layer_short = layer_dir.split("_", 1)[1] if "_" in layer_dir else layer_dir
            key = (layer_short, fm["lens"])
            with self.subTest(playbook=str(pb.relative_to(REPO_ROOT))):
                self.assertIn(key, crew_lookup, f"unknown (layer, lens): {key}")
                self.assertEqual(
                    fm["weight"],
                    crew_lookup[key],
                    f"weight mismatch for {key}: playbook={fm['weight']} crews={crew_lookup[key]}",
                )

    def test_every_playbook_framework_spec_version_matches(self):
        for pb in self.playbooks:
            fm = parse_frontmatter(pb)
            if fm is None:
                continue
            with self.subTest(playbook=str(pb.relative_to(REPO_ROOT))):
                self.assertEqual(fm["framework_spec_version"], self.framework_version)


if __name__ == "__main__":
    unittest.main()
