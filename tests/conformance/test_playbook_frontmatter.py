"""Lens playbooks' YAML frontmatter parses + matches REVIEW_CREWS.yaml.

Scope (CLEANUP-001): only `*.md` files carrying the lens-playbook contract
(`layer` + `lens` keys) are lens playbooks. Layer `README.md` overviews and the
`10_EVAL` / `10_IPVERIFY` operational playbooks (`name`-keyed frontmatter, no
`lens`) are a different contract and are excluded here — not weakened, scoped.
"""

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


def is_lens_playbook(path: Path) -> bool:
    """A lens playbook declares the (`layer`, `lens`) contract in frontmatter."""
    if path.name == "README.md":
        return False
    fm = parse_frontmatter(path)
    if fm is None or "layer" not in fm or "lens" not in fm:
        return False
    # `type: process-playbook` files are operational guides, not review lenses.
    return fm.get("type") != "process-playbook"


class PlaybookFrontmatterTests(unittest.TestCase):
    def setUp(self):
        with CREWS_PATH.open() as f:
            self.crews = yaml.safe_load(f)
        self.framework_version = VERSION_PATH.read_text().strip()
        if PLAYBOOKS_DIR.exists():
            self.playbooks = [p for p in PLAYBOOKS_DIR.rglob("*.md") if is_lens_playbook(p)]
        else:
            self.playbooks = []

    def test_lens_playbook_set_is_nonempty(self):
        """Guards the guard: an empty scope would pass every assertion below vacuously."""
        self.assertGreater(
            len(self.playbooks), 0, "no lens playbooks found — scope predicate is broken"
        )

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
