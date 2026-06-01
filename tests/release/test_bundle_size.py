"""Release: bundle stays under marketplace size cap."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root

LIMITS = yaml.safe_load(
    (Path(__file__).resolve().parent / "limits.yaml").read_text(encoding="utf-8")
)


def bundle_size_bytes(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


class BundleSizeTests(unittest.TestCase):
    def test_bundle_under_cap(self):
        size = bundle_size_bytes(plugin_bundle_root())
        self.assertLessEqual(
            size,
            LIMITS["bundle_max_bytes"],
            f"bundle {size} bytes exceeds cap {LIMITS['bundle_max_bytes']}",
        )

    def test_skill_count_under_cap(self):
        n_skills = len([d for d in (plugin_bundle_root() / "skills").iterdir() if d.is_dir()])
        self.assertLessEqual(n_skills, LIMITS["manifest_max_skill_count"])
