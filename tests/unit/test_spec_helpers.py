"""Unit: tests/conformance/_spec.py helper extensions."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import ARTIFACTS, layer_root, template_path


class SpecHelperTests(unittest.TestCase):
    def test_layer_root_returns_existing_directory_for_each_artifact(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                root = layer_root(name)
                self.assertTrue(root.exists(), f"missing layer dir for {name}: {root}")
                self.assertTrue(root.is_dir())

    def test_template_path_resolves_for_each_artifact(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                tpl = template_path(name)
                self.assertTrue(tpl.exists(), f"missing template: {tpl}")
                self.assertEqual(tpl.suffix, ".yaml")


if __name__ == "__main__":
    unittest.main()
